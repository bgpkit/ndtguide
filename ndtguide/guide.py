class NDTGuide:
    client = None

    def login(self):
        from google.colab import auth
        auth.authenticate_user()
        print('Authenticated')
        from google.cloud import bigquery
        self.client = bigquery.Client(project="measurement-lab")

    def get_client(self):
        return self.client

    @staticmethod
    def get_table_path(table_name: str):
        """
        Get table's BigQuery full path from table name.

        Supported table names include:
        - "ndt5"
        - "ndt7"
        """
        namespace = "measurement-lab.ndt"
        tables = ["ndt5", "ndt7"]
        assert table_name in tables

        return f"{namespace}.{table_name}"

    def exec_sql(self, sql: str):
        return self.client.query(sql).to_dataframe()

    def sql_daily_aggregate(
            self,
            table_name: str,
            date_start: str, date_end: str, aggr_func: str,
            client_asn: str = None, client_cidr: str = None, client_country: str = None,
            server_asn: str = None, server_cidr: str = None, server_country: str = None,
    ):
        assert aggr_func in ["avg", "min", "max"]
        assert date_start is not None and date_start != ""
        assert date_end is not None and date_end != ""
        table_path = self.get_table_path(table_name)

        where_str = ""
        if client_asn is not None and client_asn != "":
            where_str += f" and client.Network.ASNumber={client_asn}"
        if client_cidr is not None and client_cidr != "":
            where_str += f" and client.Network.CIDR='{client_cidr}'"
        if client_country is not None and client_country != "":
            where_str += f" and client.Geo.CountryCode='{client_country.upper()}'"

        if server_asn is not None and server_asn != "":
            where_str += f" and server.Network.ASNumber={server_asn}"
        if server_cidr is not None and server_cidr != "":
            where_str += f" and server.Network.CIDR='{server_cidr}'"
        if server_country is not None and server_country != "":
            where_str += f" and server.Geo.CountryCode='{server_country.upper()}'"

        return f"""
      SELECT {aggr_func}(a.MeanThroughputMbps) as {aggr_func}_throughput, {aggr_func}(a.MinRTT) as {aggr_func}_rtt, {aggr_func}(a.lossrate) as {aggr_func}_lossrate, date,
      FROM `{table_path}` 
      WHERE a.MeanThroughputMbps>0 and a.MinRTT >0 and a.lossrate>0 and
          date>='{date_start}' and date<='{date_end}' {where_str}
      GROUP BY date ORDER BY date;
      """

    def sql_get_servers(self, table_name: str, date_start, date_end, client_asn: str = None):
        table_path = self.get_table_path(table_name)
        where_str = f" and client.Network.ASNumber={client_asn}"
        if client_asn is None or client_asn == "":
            where_str = ""

        return f"""
      SELECT distinct server.Site, server.Machine, server.Network.ASNumber, server.Network.ASName, server.Network.CIDR, server.Geo.CountryCode, server.Geo.City
      FROM `{table_path}` 
      WHERE date>='{date_start}' and date<='{date_end}' {where_str}
      """

    def sql_get_clients(self, table_name: str, date_start, date_end, server_asn: str = None):
        table_path = self.get_table_path(table_name)
        where_str = f" and client.Network.ASNumber={server_asn}"
        if server_asn is None or server_asn == "":
            where_str = ""
        return f"""
      SELECT distinct client.Network.ASNumber, client.Network.ASName, client.Geo.CountryCode
      FROM `{table_path}` 
      WHERE date>='{date_start}' and date<='{date_end}' {where_str}
      """

    @staticmethod
    def get_schema():
        return {
            "id": "string",
            "date": "date",
            "server": {
                "Site": "string",
                "Machine": "string",
                "Geo": {
                    "CountryCode": "string",
                    "CountryName": "string",
                    "City": "string",
                    "ContinentCode": "string",
                },
                "Network": {
                    "CIDR": "string",
                    "ASNumber": "integer",
                    "ASName": "string"
                }
            },
            "client": {
                "Geo": {
                    "CountryCode": "string",
                    "CountryName": "string",
                    "City": "string",
                    "ContinentCode": "string",
                },
                "Network": {
                    "CIDR": "string",
                    "ASNumber": "integer",
                    "ASName": "string"
                }
            },
            "a": {
                "UUID": "string",
                "CongestionControl": "string",
                "TestTime": "TimeStamp",
                "MeanThroughputMbps": "float",
                "MinRTT": "float",
                "LossRate": "float"
            }
        }
