#!/bin/env python
#-*- coding: utf-8 -*-


def tidy_pem_64c_per_line(key, header, footer):
    start = 0
    key_tidy = ''
    while start < len(key):
        if start + 64 > len(key):
            key_tidy += key[start : start + len(key)]
        else:
            key_tidy += key[start : (start + 64)] + '\n'
        start += 64
    return header + '\n' + key_tidy + '\n' + footer
 
 
if __name__ == '__main__':
    key="MIICXAIBAAKBgQCtvEajTikMGBNvVRAvaWDAyTWDzZWPtNlOUIz+Fwdo/3pWVHmZZSJ2FW5jZ0z3REff5c66Z6LLVHndmDUlrTdrU/XXCoYj60PJhYJhMb8QZ5c9+z61y+sEt6ZzroIZPkiivrfS2gsGsdvlj75ISEFmSI7y2ABxthhaxZZLizQjQQIDAQABAoGAWsCwvXmEo5aoAE4U6E9JhSsV00W+zJSRtwEIxWnOKyDZDOOPqXtU5w4G3dIGOFvol6J5vJGKTmBQUFrD2GyFN6Re3bAvdKb5VEKm+NmpUz2Cu1iMdKIr76+/+b6qggZVtfcPqH5KBvK9mF1iTCBDizpUM3UeOAYRzNYeBHRqOOECQQDkK/6CNOEsFsffgt8mTLL9y3Gl4vFUobOgnw+A2PwhThnRUwFnTohwXVUgFPxv27IJCMSTgqcA7I8ZKTFA8/BlAkEAwuyppyIJ6UMG+Q3LaeB+S4aLxjPAaIF2VR0BoRLFnWv87zTQJb1Od003aVCoB3scGlFypqY5WWctvWy1pguDrQJBANxk3l5Yw5M5ofB0UiWFenMJOwpX7nGoC4C/g1MaxFdLQEbf3YAy7DlU/a+Sdc96LzrovDAbyEJtPT+5eTjbJ70CQB8bm9ujcAd8/fDjRbJI9H7jIw1nlu5WsubUcT0efNEpub0HJazQMGSTuyMgjyBaglqk4vI7lu1wrPkND1RHhCUCQElSUfodnKI8eE9JWKBaY3dfwb4zFWGUKpwtuWe5si6fywImAGdIQ6V0m/p50v9DNMVZ0yvcIEgnunVczIpAgj8="
    print(tidy_pem_64c_per_line(key, '-----BEGIN RSA PRIVATE KEY-----', '-----END RSA PRIVATE KEY-----'))
