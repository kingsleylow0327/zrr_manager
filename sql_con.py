import aiomysql
import asyncio
from mysql.connector import pooling
from logger import Logger
from dto.license_dto import LicenseDTO
import datetime

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
        self.async_pool = None
 
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
    
    async def init_async_pool(self):
        self.async_pool = await aiomysql.create_pool(
            host=self.config.DB_ADDRESS,
            port=int(self.config.DB_PORT),
            user=self.config.DB_USERNAME,
            password=self.config.DB_PASSWORD,
            db=self.config.DB_SCHEMA,
            minsize=1,
            maxsize=int(self.config.POOL_SIZE),
            autocommit=True
        )
        logger.info("Async DB Pool Created")
    
    def dbcon_manager(self, sql:str, get_all=False):
        connection_object = self.pool.get_connection()
        row = None
        try:
            with connection_object.cursor(dictionary=True) as cursor:
                cursor.execute(sql)
                row = cursor.fetchall() if get_all else cursor.fetchone()
                connection_object.commit()
        except Exception as e:
            logger.warning(sql)
            logger.warning(e)
        finally:
            connection_object.close()
        if not row:
            return None
        return row
    
    async def async_dbcon_manager(self, sql: str, get_all=False):
        async with self.async_pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                try:
                    await cursor.execute(sql)
                    row = await cursor.fetchall() if get_all else await cursor.fetchone()
                    return row if row else None
                except Exception as e:
                    logger.warning(sql)
                    logger.warning(e)
                    return None
    
    def get_trader_list(self, following_trader_id=None):
        sql = f"""SELECT t.*, f.count FROM {self.config.TRADER_CHANNEL_TABLE} as t
        LEFT JOIN (SELECT player_id, COUNT(player_id)-1 as count FROM {self.config.FOLLOWER_TABLE}
        GROUP BY player_id) as f
        on f.player_id = t.trader_id
        WHERE t.is_hidden = 0
        """
        if following_trader_id:
            sql = f"""SELECT t.*, f.count FROM {self.config.TRADER_CHANNEL_TABLE} as t
            LEFT JOIN (SELECT player_id, COUNT(player_id)-1 as count FROM {self.config.FOLLOWER_TABLE}
            GROUP BY player_id) as f
            on f.player_id = t.trader_id
            WHERE
            trader_id != '{following_trader_id}'
            AND
            t.is_hidden = 0
            """
        return self.dbcon_manager(sql, get_all=True)
    
    def get_trader_by_id(self, follower_id):
        sql = f"""SELECT trader_name FROM {self.config.FOLLOWER_TABLE} as f
        LEFT JOIN {self.config.TRADER_CHANNEL_TABLE} as t
        ON f.player_id = t.trader_id
        WHERE f.follower_id = '{follower_id}'
        """
        return self.dbcon_manager(sql, get_all=False)
    
    def update_trader_by_trader_name(self, trader_name, follower_id):
        sql = f"""UPDATE {self.config.FOLLOWER_TABLE}
        SET player_id = (SELECT if(INSTR(trader_id, ',') > 0,trader_name,trader_id)
        FROM {self.config.TRADER_CHANNEL_TABLE} where trader_name = '{trader_name}'), following_time = NOW()
        WHERE 
        follower_id = '{follower_id}'
        AND player_id != follower_id"""
        return self.dbcon_manager(sql, get_all=True)
    
    def cancel_trader(self, follower_id):
        sql = f"""UPDATE {self.config.FOLLOWER_TABLE}
        SET player_id = ''
        WHERE 
        follower_id = '{follower_id}'
        AND player_id != follower_id"""
        return self.dbcon_manager(sql, get_all=True)
    
    def update_trader_list(self, player_id, follower_id):
        sql = f"""UPDATE {self.config.FOLLOWER_TABLE}
        SET player_id = '{player_id}', following_time = NOW()
        WHERE 
        follower_id = '{follower_id}'
        AND player_id != follower_id
        """
        return self.dbcon_manager(sql, get_all=True)
    
    def get_expired_user(self):
        sql = f"""SELECT a.player_id, a.discord_id, a.expiry_date, t.trader_name FROM {self.config.API_TABLE} as a
        LEFT JOIN {self.config.FOLLOWER_TABLE} as f
        ON a.player_id = f.follower_id
        LEFT JOIN {self.config.TRADER_CHANNEL_TABLE} as t
        ON f.player_id = t.trader_id
        WHERE a.expiry_date <= NOW() AND (f.player_id IS NOT NULL AND f.player_id != '')
        """
        return self.dbcon_manager(sql, get_all=True)
    
    def get_expired_vip_user(self, table_name):
        sql = f"""SELECT * FROM {table_name} where expired_date <= NOW() and discord_id IS NOT NULL and status = 'vip'
        """
        return self.dbcon_manager(sql, get_all=True)
    
    def remove_vip_flag(self, table_name, uuid_list):
        sql = f"""UPDATE {table_name}
        SET status = null
        WHERE uuid IN {uuid_list}
        """
        return self.dbcon_manager(sql, get_all=True)
    
    def unfollow_trader(self, player_list):
        sql = f"""UPDATE {self.config.FOLLOWER_TABLE}
        SET player_id = ''
        WHERE follower_id IN {player_list}
        """
        return self.dbcon_manager(sql, get_all=True)

    def update_damage_cost(self, damage_cost, account_name):
        sql = f"""UPDATE {self.config.FOLLOWER_TABLE}
        SET damage_cost = '{damage_cost}'
        WHERE 
        follower_id = '{account_name}'
        AND player_id != follower_id
        """
        return self.dbcon_manager(sql, get_all=True)
    
    def get_all_player_status(self, player_id, product="atm"):
        sql = f"""SELECT a.player_id, a.api_key, a.api_secret, ifnull(t.trader_name, f.player_id) as trader_name, f.player_id as trader_discord_id, f.following_time, f.damage_cost, a.expiry_date
        FROM {self.config.API_TABLE} as a
        LEFT JOIN {self.config.FOLLOWER_TABLE} as f
        ON a.player_id = f.follower_id
        LEFT JOIN {self.config.TRADER_CHANNEL_TABLE} as t
        ON f.player_id = t.trader_id
        WHERE
        a.discord_id = '{player_id}'
        and
        f.type = '{product}';
        """
        return self.dbcon_manager(sql, get_all=True)
    
    def get_api_secret_by_account_name(self, player_id, account_name):
        sql = f"""SELECT a.api_key, a.api_secret
        FROM {self.config.API_TABLE} as a
        WHERE
        a.discord_id = '{player_id}'
        AND
        a.player_id = '{account_name}';
        """
        return self.dbcon_manager(sql, get_all=False)
    
    def set_player_api(self, player_id, api, key, player_account_name):    
        sql = f"""UPDATE {self.config.API_TABLE}
        SET api_key = '{api}', api_secret = '{key}'
        WHERE 
        player_id = '{player_account_name}'
        AND
        discord_id = '{player_id}'
        """
        return self.dbcon_manager(sql, get_all=True)
    
    def is_admin(self, player_id):
        sql = f"""SELECT discord_id FROM user 
        WHERE discord_id='{player_id}'"""
        ret = self.dbcon_manager(sql, get_all=True)
        if not ret:
            return False
        return len(ret) != 0
    
    def is_vip_admin(self, player_id):
        sql = f"""SELECT discord_id FROM vip_admin 
        WHERE discord_id='{player_id}'"""
        ret = self.dbcon_manager(sql, get_all=True)
        if not ret:
            return False
        return len(ret) != 0
    
    def check_user_exist_with_ref(self, player_id, player_account_name):
        sql = f"""SELECT player_id FROM {self.config.API_TABLE}
        WHERE (player_id='{player_account_name}')
        OR
        (player_id='{player_account_name}'
        AND
        discord_id='{player_id}')"""
        ret = self.dbcon_manager(sql, get_all=True)
        return ret and len(ret) != 0
    
    def check_user_exist(self, player_id):
        sql = f"""SELECT player_id FROM {self.config.API_TABLE} 
        WHERE discord_id='{player_id}'"""
        ret = self.dbcon_manager(sql, get_all=True)
        return ret and len(ret) != 0
    
    def activate_user(self, player_id, player_account_name, expiry, type="atm"):
        sql = f"""INSERT INTO {self.config.API_TABLE}
        (player_id, discord_id, expiry_date, platform)
        VALUES
        ('{player_account_name}', '{player_id}', date_add(now(),interval {expiry}), 'bingx')
        """
        self.dbcon_manager(sql)

        sql = f"""INSERT INTO {self.config.FOLLOWER_TABLE}
        (follower_id, platform, type)
        VALUES
        ('{player_account_name}', 'bingx', '{type}')"""
        return self.dbcon_manager(sql)
    
    def extend_user(self, player_account_name, expiry):
        sql = f"""UPDATE {self.config.API_TABLE}
        SET expiry_date = IF(expiry_date < NOW(), DATE_ADD(NOW(), INTERVAL {expiry}), DATE_ADD(expiry_date, INTERVAL {expiry}))
        WHERE player_id = '{player_account_name}';
        """
        return self.dbcon_manager(sql)
    
    def register_license(self, dto:LicenseDTO, account_used):
        sql = f"""INSERT INTO {self.config.LICENSE_TABLE}
        (player_id, license_key, validity, type, trader_name, account_used)
        VALUES
        ('{dto.userId}', '{dto.licenseKey}', '{dto.validity}', '{dto.type}', '{dto.trader}', '{account_used}')"""
        return self.dbcon_manager(sql)
    
    def get_license_by_license_key(self, license_key):
        sql = f"""SELECT * FROM {self.config.LICENSE_TABLE}
        WHERE license_key = '{license_key}'
        ORDER BY id DESC
        limit 1"""
        return self.dbcon_manager(sql, get_all=False)
    
    def get_license(self, user_id):
        sql = f"""SELECT * FROM {self.config.LICENSE_TABLE}
        WHERE player_id = '{user_id}'"""
        return self.dbcon_manager(sql, get_all=True)
    
    def use_license(self, license_key):
        sql = f"""UPDATE {self.config.LICENSE_TABLE}
        SET time_used = NOW()
        WHERE license_key = '{license_key}'"""
        return self.dbcon_manager(sql)

    # TRADE_VOLUME_TABLE
    def check_uid_exist_from_trade_volume_table(self, uid):
        sql = f"""
        SELECT id FROM {self.config.TRADE_VOLUME_TABLE} 
        WHERE uuid='{uid}'"""
        ret = self.dbcon_manager(sql, get_all=True)
        return ret and len(ret) != 0
    
    def check_discord_id_exist_from_trade_volume_table(self, discord_id):
        sql = f"""
        SELECT id FROM {self.config.TRADE_VOLUME_TABLE} 
        WHERE discord_id='{discord_id}'"""
        ret = self.dbcon_manager(sql, get_all=True)
        return ret and len(ret) != 0
    
    def get_trade_volume_table_by_uuid(self, uuid):
        sql = f"""
        SELECT * FROM {self.config.TRADE_VOLUME_TABLE} 
        WHERE uuid='{uuid}'"""
        return self.dbcon_manager(sql, get_all=False)
    
    def get_bitget_table_by_uuid(self, uuid):
        sql = f"""
        SELECT * FROM {self.config.BITGET_TABLE} 
        WHERE uuid='{uuid}'"""
        return self.dbcon_manager(sql, get_all=False)
    
    def check_uuid_exist_from_propw_table(self, uuid):
        sql = f"""
        SELECT propw_uid FROM {self.config.PROPW_TABLE} 
        WHERE propw_uid='{uuid}'
        AND discord_id is NULL"""
        ret = self.dbcon_manager(sql, get_all=True)
        return ret and len(ret) != 0
    
    def check_uuid_exist_from_bitget_table(self, uuid):
        sql = f"""
        SELECT uuid FROM {self.config.BITGET_TABLE} 
        WHERE uuid='{uuid}'
        AND discord_id is NULL"""
        ret = self.dbcon_manager(sql, get_all=True)
        return ret and len(ret) != 0
    
    def check_uuid_exist_from_pionex_table(self, uuid):
        sql = f"""
        SELECT pionex_uid FROM {self.config.PIONEX_TABLE} 
        WHERE pionex_uid='{uuid}'
        AND discord_id is NULL"""
        ret = self.dbcon_manager(sql, get_all=True)
        return ret and len(ret) != 0

    def get_trade_volume_by_id(self, discord_id):
        sql = f"""
        SELECT * FROM {self.config.TRADE_VOLUME_TABLE} 
        WHERE discord_id='{discord_id}'"""
        return self.dbcon_manager(sql)
    
    def get_propw_by_id(self, discord_id):
        sql = f"""
        SELECT * FROM {self.config.PROPW_TABLE} 
        WHERE discord_id='{discord_id}'"""
        return self.dbcon_manager(sql)
    
    def get_bitget_by_id(self, discord_id):
        sql = f"""
        SELECT * FROM {self.config.BITGET_TABLE} 
        WHERE discord_id='{discord_id}'"""
        return self.dbcon_manager(sql)
    
    def get_pionex_by_id(self, discord_id):
        sql = f"""
        SELECT * FROM {self.config.PIONEX_TABLE} 
        WHERE discord_id='{discord_id}'"""
        return self.dbcon_manager(sql)
    
    def update_expiry_date_by_discord_id(self, discord_id, expiry_date):
        sql = f"""
        UPDATE {self.config.TRADE_VOLUME_TABLE}
        SET expired_date = '{expiry_date}'
        WHERE discord_id ='{discord_id}'"""
        return self.dbcon_manager(sql)
    
    def insert_user_into_trade_volume_table(self, uuid, discord_id, date):
        sql = f"""
        INSERT INTO {self.config.TRADE_VOLUME_TABLE}
        (uuid, discord_id, expired_date)
        VALUES
        ('{uuid}', '{discord_id}', '{date}')"""
        return self.dbcon_manager(sql)
    
    def insert_solely_uid(self, uuid):
        sql = f"""
        INSERT INTO {self.config.TRADE_VOLUME_TABLE}
        (uuid)
        VALUES
        ('{uuid}')"""
        return self.dbcon_manager(sql)

    def update_user_from_trade_volume_table(self, uuid, discord_id):
        sql = f"""
        UPDATE {self.config.TRADE_VOLUME_TABLE}
        SET discord_id = '{discord_id}'
        WHERE uuid ='{uuid}'"""
        return self.dbcon_manager(sql)
    
    def update_user_from_vip_tables_with_date(self, table, uuid, discord_id, date):
        sql = f"""
        UPDATE {table}
        SET discord_id = '{discord_id}', expired_date = '{date}', status = 'vip'
        WHERE uuid ='{uuid}'"""
        return self.dbcon_manager(sql)
    
    def update_user_from_propw_table_with_date(self, uuid, discord_id, date):
        sql = f"""
        UPDATE {self.config.PROPW_TABLE}
        SET discord_id = '{discord_id}', expired_date = '{date}'
        WHERE propw_uid ='{uuid}'"""
        return self.dbcon_manager(sql)
    
    def update_user_from_bitget_table_with_date(self, uuid, discord_id, date):
        sql = f"""
        UPDATE {self.config.BITGET_TABLE}
        SET discord_id = '{discord_id}', expired_date = '{date}', status = 'vip'
        WHERE uuid ='{uuid}'"""
        return self.dbcon_manager(sql)
    
    def update_user_from_pionex_table_with_date(self, uuid, discord_id, date):
        sql = f"""
        UPDATE {self.config.PIONEX_TABLE}
        SET discord_id = '{discord_id}', expired_date = '{date}'
        WHERE pionex_uid ='{uuid}'"""
        return self.dbcon_manager(sql)

    def fetch_user_trade_volume_by_discord_id(self, discord_id):
        sql = f"""
        SELECT volume FROM {self.config.TRADE_VOLUME_TABLE} 
        WHERE discord_id='{discord_id}'"""
        return self.dbcon_manager(sql)

    def fetch_vips_by_expiry(self, days=0):
        if days == 0:
            sql = f"""
            SELECT discord_id
            FROM {self.config.TRADE_VOLUME_TABLE}
            WHERE DATE(expired_date) = CURDATE()
            """
        else:
            sql = f"""
            SELECT discord_id
            FROM {self.config.TRADE_VOLUME_TABLE}
            WHERE DATE(expired_date) = DATE_ADD(CURDATE(), INTERVAL {days} DAY)
            """

        result = self.dbcon_manager(sql, get_all=True)
        return [row['discord_id'] for row in result] if result else []

    # strategies
    def set_follower_strategy(self, strategy_list, follower_id):
        sql = """
        INSERT INTO {} (player_id, follower_id, platform, type) 
        VALUES ('{}', '{}', '{}', {});
        """.format(
            self.config.FOLLOWER_TABLE, strategy_list, follower_id, 'bingx', 1
        )

        return self.dbcon_manager(sql)

    def update_follower_strategy(self, strategy_list, follower_id):
        sql = f"""
            UPDATE {self.config.FOLLOWER_TABLE}
            SET player_id = '{strategy_list}', following_time = NOW()
            WHERE 
            follower_id = '{follower_id}'
            AND platform = 'bingx'
            AND type = 'strategy'
            """

        return self.dbcon_manager(sql, get_all=True)

    def clear_follower_strategy(self, follower_id):
        sql = f"""
        UPDATE {self.config.FOLLOWER_TABLE}
        SET player_id = ''
        WHERE 
        follower_id = '{follower_id}'
        AND platform = 'bingx'
        AND type = 'strategy'
        """

        return self.dbcon_manager(sql)

    def get_all_active_strategies(self):
        sql = f"""
        SELECT id, name FROM {self.config.STRATEGIES_TABLE}
        WHERE 
        deleted_at IS NULL
        """

        return self.dbcon_manager(sql, get_all=True)

    def get_active_strategy_where(self, attribute, data):
        sql = f"""
        SELECT * FROM {self.config.STRATEGIES_TABLE}
        WHERE 
        deleted_at is NULL
        AND {attribute} = {data}
        """

        return self.dbcon_manager(sql)

    async def update_bitget_table(self, tupples):
        sql_format = """INSERT INTO bitget_table (uuid, volume) VALUES ('{}', '{}') ON DUPLICATE KEY UPDATE volume = VALUES(volume);"""
        queries = [sql_format.format(self.config.TRADE_VOLUME_TABLE, t[0], t[1]) for t in tupples]
        tasks = [self.async_dbcon_manager(query, get_all=True) for query in queries]
        await asyncio.gather(*tasks)
        now = datetime.datetime.now()
        logger.info(f"BITGET Table Update Done at, {now}")
    
    def update_pionex_table(self, tupples):
        sql_format = """INSERT INTO {} (pionex_uid, amount) VALUES ('{}', '{}') ON DUPLICATE KEY UPDATE pionex_uid = VALUES(pionex_uid), amount = VALUES(amount);"""
        for t in tupples:
            self.dbcon_manager(sql_format.format(self.config.PIONEX_TABLE, t[0], t[1]))
        now = datetime.datetime.now()
        logger.info(f"Pionex Table Update Done at, {now}")
    
    def update_propw_table(self, tupples):
        sql_format = """INSERT INTO {} (propw_uid, amount) VALUES ('{}','{}') ON DUPLICATE KEY UPDATE amount = VALUES(amount);"""
        for t in tupples:
            self.dbcon_manager(sql_format.format(self.config.PROPW_TABLE, t[0], t[1]))
        now = datetime.datetime.now()
        logger.info(f"PropW Table Update Done at, {now}")
    
    async def update_bingx_table(self, tupples):
        sql_format = """INSERT INTO {} (uuid, volume) VALUES ('{}', '{}') ON DUPLICATE KEY UPDATE volume = VALUES(volume);"""
        queries = [sql_format.format(self.config.TRADE_VOLUME_TABLE, t[0], t[1]) for t in tupples]
        tasks = [self.async_dbcon_manager(query, get_all=True) for query in queries]
        await asyncio.gather(*tasks)
        now = datetime.datetime.now()
        logger.info(f"BingX Table Update Done at, {now}")

    async def update_bitget_table(self, tupples):
        sql_format = """INSERT INTO {} (uuid, volume) VALUES ('{}', '{}') ON DUPLICATE KEY UPDATE volume = VALUES(volume);"""
        queries = [sql_format.format(self.config.BITGET_TABLE, t[0], t[1]) for t in tupples]
        tasks = [self.async_dbcon_manager(query, get_all=True) for query in queries]
        await asyncio.gather(*tasks)
        now = datetime.datetime.now()
        logger.info(f"BingX Table Update Done at, {now}")
    
    def get_bingx_table_with_volume(self, amount):
        sql = f"""SELECT discord_id FROM {self.config.TRADE_VOLUME_TABLE} where discord_id IS NOT NULL and volume >= {amount};"""
        return self.dbcon_manager(sql, get_all=True)
    
    def get_bitget_table_with_volume(self, amount):
        sql = f"""SELECT discord_id FROM {self.config.BITGET_TABLE} where discord_id IS NOT NULL and volume >= {amount};"""
        return self.dbcon_manager(sql, get_all=True)
    
    def get_propw_table_with_uid(self):
        sql = f"""SELECT * FROM {self.config.PROPW_TABLE} where discord_id IS NOT NULL;"""
        return self.dbcon_manager(sql, get_all=True)
    
    def give_bingx_vip(self, user_list, day_interval):
        sql = f"""UPDATE {self.config.TRADE_VOLUME_TABLE} set expired_date = DATE_ADD(NOW(), INTERVAL {day_interval} DAY), status = 'vip' where discord_id in ({user_list})"""
        return self.dbcon_manager(sql)
    
    def update_bingx_table_expired_date(self, user_list, day_interval):
        sql = f"""UPDATE {self.config.TRADE_VOLUME_TABLE} set expired_date = DATE_ADD(NOW(), INTERVAL {day_interval} DAY), status = 'vip' where discord_id in ({user_list})"""
        return self.dbcon_manager(sql)
    
    def update_bitget_table_expired_date(self, user_list, day_interval):
        sql = f"""UPDATE {self.config.BITGET_TABLE} set expired_date = DATE_ADD(NOW(), INTERVAL {day_interval} DAY), status = 'vip' where discord_id in ({user_list})"""
        return self.dbcon_manager(sql)
    
    def update_x_expired_date_by_discord_id(self, table, discord_id, expiry_date):
        sql = f"""
        UPDATE {table}
        SET expired_date = '{expiry_date}'
        WHERE discord_id ='{discord_id}'"""
        return self.dbcon_manager(sql)
    
    def get_from_channel_table(self, key):
        sql = f"""SELECT * FROM channel_table where name = '{key}';"""
        return self.dbcon_manager(sql)
    
    def update_channel_table(self, key, message_id):
        sql = f"""
        UPDATE channel_table
        SET message_id = '{message_id}'
        WHERE name = '{key}'"""
        return self.dbcon_manager(sql)