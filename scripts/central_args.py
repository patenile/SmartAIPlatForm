#!/usr/bin/env python3
"""
Centralized argument parser for all SmartAIPlatform scripts.
"""
import argparse

def get_arg_parser():
    parser = argparse.ArgumentParser(description="SmartAIPlatform unified CLI")
    parser.add_argument('--debug', action='store_true', help='Enable debug logging for all components')
    parser.add_argument('--list-categories', action='store_true', help='List only available categories')
    # Add more global arguments here as needed
    return parser
