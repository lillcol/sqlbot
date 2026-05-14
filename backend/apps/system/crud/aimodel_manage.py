
from apps.system.models.system_model import AiModelDetail
from common.core.db import engine
from sqlmodel import Session, select
from common.utils.crypto import sqlbot_encrypt
from common.utils.utils import SQLBotLogUtil


def _is_plain_api_domain(value: str | None) -> bool:
    return bool(value and value.startswith("http"))


def _is_plain_api_key(value: str | None) -> bool:
    return bool(value and value.startswith("sk-"))


async def async_model_info():
    with Session(engine) as session:
        model_list = session.exec(select(AiModelDetail)).all()
        any_model_change = False
        if model_list:
            for model in model_list:
                current_model_change = False
                try:
                    if _is_plain_api_key(model.api_key):
                        model.api_key = await sqlbot_encrypt(model.api_key)
                        any_model_change = True
                        current_model_change = True
                    if _is_plain_api_domain(model.api_domain):
                        model.api_domain = await sqlbot_encrypt(model.api_domain)
                        any_model_change = True
                        current_model_change = True
                except Exception as e:
                    SQLBotLogUtil.error(f"AI model secret migration skipped for model {model.id}: {e}")
                if model.supplier and model.supplier == 12:
                    model.supplier = 15
                    any_model_change = True
                    current_model_change = True
                if current_model_change:
                    session.add(model)
        if any_model_change:
            session.commit()
            SQLBotLogUtil.info("✅ 异步加密已有模型的密钥和地址完成")           
            
            
        