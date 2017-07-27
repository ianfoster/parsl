#!/bin/sh

# MKDOC
# Convenience script to render the doc

cd $( dirname $0 )

rst2pdf README.rst
