#!/bin/bash

search_dir=installs
for entry in "$search_dir"/*
do
	bash $entry
done