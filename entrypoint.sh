#!/bin/bash
gunicorn -b:5000 python app.py
