# -*- coding: utf-8 -*-


def clean_none(data: dict) -> dict:
    return {
        k: v
        for k, v in data.items()
        if v is not None
    }
