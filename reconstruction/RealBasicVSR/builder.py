import torch.nn as nn
from mmcv import build_from_cfg
from mmedit.models.registry import BACKBONES, COMPONENTS, LOSSES, MODELS
import boto3


class Builder:
    
    def __init__(self) -> None:
        pass

    def build(self,cfg, registry, default_args=None):
        """Build module function.

        Parameters
        ----------
            cfg: dict
                Configuration for building modules.
            registry: obj
                ``registry`` object.
            default_args: dict
                Default arguments. Defaults to None.
        """
        if isinstance(cfg, list):
            modules = [self.build_from_cfg(cfg_, registry, default_args) for cfg_ in cfg]
            return nn.Sequential(*modules)

        return self.build_from_cfg(cfg, registry, default_args)


    def build_backbone(self,cfg):
        """Build backbone.

        Parameters
        ----------
            cfg: dict
                Configuration for building backbone.
        """
        return self.build(cfg, BACKBONES)


    def build_component(self,cfg):
        """Build component.

        Parameters
        ----------
            cfg: dict
                Configuration for building component.
        """
        return self.build(cfg, COMPONENTS)


    def build_loss(self,cfg):
        """Build loss.

        Parameters
        ----------
            cfg: dict
                Configuration for building loss.
        """
        return self.build(self,cfg, LOSSES)


    def build_model(self,cfg, train_cfg=None, test_cfg=None):
        """Build model.

        Parameters
        ----------
            cfg: dict
                Configuration for building model.
            train_cfg: dict
                Training configuration. Default: None.
            test_cfg: dict
                Testing configuration. Default: None.
        """
        return self.build(cfg, MODELS, dict(train_cfg=train_cfg, test_cfg=test_cfg))


    def download_model(self,local_path, bucket_name, key):
        """
        Downloads any model file from s3 to a local path.

        Parameters
        ----------

        local_path: string
            Path where we want to store object locally
        bucket_name: string
            The bucket name where the files belong in the S3 bucket.
        key: string
            The name of the object and any preceeding folders.
        """
        s3 = boto3.client("s3")
        with open(local_path, "wb") as file:
            s3.download_fileobj(bucket_name, key, file)
        return print(f"Downloaded file to: {local_path}")
