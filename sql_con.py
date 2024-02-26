from mysql.connector import pooling
from logger import Logger

# Logger setup
logger_mod = Logger("DB")
logger = logger_mod.get_logger()

class ZonixDB():
    def __init__(self, config):
        self.config = config
        self.pool = self._create_pool(config.DB_ADDRESS,
            config.DB_PORT,
            config.DB_SCHEMA,
            config.DB_USERNAME,
            config.DB_PASSWORD,
            config.POOL_SIZE)
 
    def _create_pool(self, host, port, database, user, password, size):
        try:
            pool = pooling.MySQLConnectionPool(pool_name="zrr_pool",
                pool_size=int(size),
                pool_reset_session=True,
                host=host,
                port=port,
                database=database,
                user=user,
                password=password)
            
            logger.info("DB Pool Created")
            return pool

        except Exception as e:
            logger.warning(e)
            logger.warning("DB Pool Failed")
            return None
    
    def dbcon_manager(self, sql, get_all=False):
        connection_object = self.pool.get_connection()
        row = None
        with connection_object as connection:
            with connection.cursor(dictionary=True) as cursor:
                try:
                    cursor.execute(sql)
                    row = cursor.fetchall() if get_all else cursor.fetchone()
                    connection.commit()
                except Exception as e:
                    logger.warning(sql)
                    logger.warning(e)
        if not row:
            return None
        return row
    
    def get_trader_list(self):
        sql = f"""SELECT *
        FROM {self.config.TRADER_DETAIL_TABLE}
        """
        return self.dbcon_manager(sql, get_all=True)
    
    def update_trader_list(self, player_id, follower_id):
        sql = f"""UPDATE {self.config.FOLLOWER_TABLE}
        SET player_id = '{player_id}', following_time = NOW()
        WHERE 
        follower_id = '{follower_id}'
        AND player_id != follower_id
        """
        return self.dbcon_manager(sql, get_all=True)

    def get_player_status(self, player_id, arg):
        sql = f"""SELECT a.player_id, a.api_key, a.api_secret, f.player_id as trader_id, f.following_time
        FROM {self.config.API_TABLE} as a
        LEFT JOIN {self.config.FOLLOWER_TABLE} as f
        ON a.player_id = f.follower_id
        WHERE a.player_id = '{arg}'
        AND
        a.discord_id = '{player_id}';
        """
        return self.dbcon_manager(sql, get_all=False)
    
    def get_all_player_status(self, player_id):
        sql = f"""SELECT a.player_id, a.api_key, a.api_secret, t.trader_name as trader_id, f.following_time
        FROM {self.config.API_TABLE} as a
        LEFT JOIN {self.config.FOLLOWER_TABLE} as f
        ON a.player_id = f.follower_id
        LEFT JOIN {self.config.TRADER_DETAIL_TABLE} as t
        ON f.player_id = t.trader_id
        WHERE
        a.discord_id = '{player_id}';
        """
        return self.dbcon_manager(sql, get_all=True)
    
    def set_player_api(self, player_id, api, key, player_ref_id):    
        sql = f"""UPDATE {self.config.API_TABLE}
        SET api_key = '{api}', api_secret = '{key}'
        WHERE 
        player_id = '{player_ref_id}'
        AND
        discord_id = '{player_id}'
        """
        return self.dbcon_manager(sql, get_all=True)
    
    def is_admin(self, player_id):
        sql = f"""SELECT discord_id FROM user 
        WHERE discord_id='{player_id}'"""
        ret = self.dbcon_manager(sql, get_all=True)
        return len(ret) != 0
    
    def check_user_exist_with_ref(self, player_id, player_ref_name):
        sql = f"""SELECT player_id FROM {self.config.API_TABLE} 
        WHERE player_id='{player_ref_name}'
        AND
        discord_id='{player_id}'"""
        ret = self.dbcon_manager(sql, get_all=True)
        return ret and len(ret) != 0
    
    def check_user_exist(self, player_id):
        sql = f"""SELECT player_id FROM {self.config.API_TABLE} 
        WHERE discord_id='{player_id}'"""
        ret = self.dbcon_manager(sql, get_all=True)
        return ret and len(ret) != 0
    
    def activate_user(self, player_id, player_ref_name):
        sql = f"""INSERT INTO {self.config.API_TABLE}
        (player_id, discord_id, platform)
        VALUES
        ('{player_ref_name}', '{player_id}', 'bingx')
        """
        self.dbcon_manager(sql)

        sql = f"""INSERT INTO {self.config.FOLLOWER_TABLE}
        (follower_id, platform)
        VALUES
        ('{player_ref_name}', 'bingx')"""
        return self.dbcon_manager(sql)