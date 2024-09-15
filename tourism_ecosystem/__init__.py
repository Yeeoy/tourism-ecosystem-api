import pymysql

pymysql.version_info = (1, 4, 13, "final", 0)  # Avoid version conflicts
pymysql.install_as_MySQLdb()
