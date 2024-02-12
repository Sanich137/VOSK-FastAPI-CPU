from sqlalchemy import create_engine, func
from Recognizer.models import db_models as models

from Recognizer.utils.pre_start_init import paths

def make_clear_base(db):
    engine = create_engine(db, json_deserializer=False)
    Base = models.Base
    Base.metadata.create_all(engine)
    return True


# удалить базу данных
def clear_base(db):
    engine = create_engine(db)
    Base = models.Base
    Base.metadata.drop_all(engine)
    return True

if __name__ == "__main__":

    #     db = 'sqlite:///' + config.base_path + 'the_bankrupts_database.db'
    #     db_office = 'sqlite:///' + 'C:\\Users\\kojevnikov\\PycharmProjects\\Parse_Gosuslugi\\base\\' + 'the_bankrupts_database.db'
    db = 'sqlite:///' + str(paths.get("db"))
    # db_home_init = 'sqlite:///' + 'D:\\Coding\\Parse_Gosuslugi\\base\\' + 'initial.db'

    #     db = 'mysql+pymysql://akojevnikov:zb5vdbpH0LL1Hxk8@192.168.94.61/kojevnikov_db'
    #     # Test if it works
    #     engine = create_engine(SQLALCHEMY_DATABASE_URI, echo=True)
    #     # print(engine.table_names())

    try:

        # delete_table()  # Удаляем таблицу Chat_Message
        # date_or_none("2022-07-12T20:28:16.17")
        # add_new_column()
        # add_or_update()
        # get_last_date()
        # get_json_data()
        # get_order_array()
        # manual_add_client_from_config(db, client)
        # save_auth_state(db)
        clear_base(db)
        make_clear_base(db)
        # copy_base()
        # add_supplier(db_home, suplier)  # OK!
        # add_order_to_base(db, order)
        # get_pfr_docs()
        # add_new_column(db)
        # None

    except Exception as e:
        print(f'Не выполнил поставленную задачу по причине - {e}')
    else:
        print(f'Выполнил задачу без ошибок')
    # try:
    #     make_clear_base()
    # except Exception as e:
    #     print(f'Не создал базу, по причине {e}')
    # else:
    #     print(f'Создал базу по запросу пользователя')
