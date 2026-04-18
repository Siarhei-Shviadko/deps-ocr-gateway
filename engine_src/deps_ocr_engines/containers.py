from typing import Dict

from dependency_injector import containers, providers

from deps_ocr_engines.application import Application
from deps_ocr_engines.domain.entities import OCREngineInitSettings
from deps_ocr_engines.domain.services import OCRService
from deps_ocr_engines.extras import (
    DepsAuthService,
    JWTAuthService,
    StorageControllerService,
)
from deps_ocr_engines.infrastructure import engines


class Containers(containers.DeclarativeContainer):
    config = providers.Configuration()
    ocr_service: providers.Provider[OCRService] = providers.Singleton(
        OCRService,
        init_engine=config.engine.preinit,
        registered_engine=providers.Dict(
            {
                "engine": engines.EngineFactory.get_engine_name(),  # type: ignore
                "init_settings": providers.Singleton(
                    OCREngineInitSettings,
                    engines.EngineFactory.get_engine(),  # type: ignore
                    providers.List(*engines.EngineFactory.get_engine_config(config.engine)),  # type: ignore
                ),
            },
        ),
    )

    engine_settings: providers.Provider[object] = providers.Object(engines.EngineFactory.get_engine_settings)
    storage_service: providers.Provider[StorageControllerService] = providers.Singleton(
        StorageControllerService,
        file_storage_url=config.storage.file_storage_url,
        verify_ssl=config.storage.verify_ssl,
    )
    build_info: providers.Provider[Dict] = providers.Dict(
        {
            "build_tag": config.info.tag,
            "build_date": config.info.date,
            "commit_hash": config.info.hash,
        },
    )
    jwt_auth_service: providers.Singleton[JWTAuthService] = providers.Singleton(
        JWTAuthService,
        config.authentication.certs_endpoint,
        config.authentication.encryption_algorithm,
        config.authentication.verify_ssl,
    )
    deps_auth_service: providers.Singleton[DepsAuthService] = providers.Singleton(
        DepsAuthService,
        jwt_auth_service,
    )

    application: providers.Singleton[Application] = providers.Singleton(
        Application,
        ocr_service=ocr_service,
        storage_service=storage_service,
        engine_settings=engine_settings,
    )
