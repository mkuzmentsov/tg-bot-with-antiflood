from db.connection_manager import Session, TgAccount, TgMessage


def get_user_by_id(id: str):
    return Session().query(TgAccount).filter_by(id=id).first()


def insert_user(id: str, username: str, full_name: str):
    tg_account = TgAccount(id=id, username=username, fullname=full_name)
    sess = Session()
    sess.add(tg_account)
    sess.commit()

    return id


def insert_message(tg_account_id, time, text_content, binary_content):
    tg_message = TgMessage(tg_account_id=tg_account_id, time=time, text_content=text_content, binary_content=binary_content)
    sess = Session()
    sess.add(tg_message)
    sess.commit()

    return tg_message.id