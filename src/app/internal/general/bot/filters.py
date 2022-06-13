from telegram.ext import Filters

INT = Filters.regex("^[0-9]+$")
FLOATING = Filters.regex("^[0-9]*[.]?[0-9]+(?:[eE][-+]?[0-9]+)?$")
TEXT = Filters.text & ~Filters.command
IMAGE = Filters.photo
