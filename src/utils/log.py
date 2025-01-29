import logging

# Configuração do logging
logging.basicConfig(
    format="%(asctime)s '%(levelname)s' - %(funcName)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=logging.INFO,
)


def log(funcao, valor_log, tipo):
    logger = logging.getLogger(funcao)

    if tipo.lower() == "info":
        logger.info(f"{funcao} - {valor_log}")
    elif tipo.lower() == "warn":
        logger.warning(f"{funcao} - {valor_log}")
    elif tipo.lower() == "error":
        logger.error(f"{funcao} - {valor_log}")
    else:
        raise ValueError(
            f"Tipo de log '{tipo}' inválido. Use 'info', 'warn' ou 'error'."
        )
