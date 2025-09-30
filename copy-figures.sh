#!/bin/bash
cp -r ./skalpel-paper/figures/* ./figures/
cp -r ./skalpel-paper/tables/* ./tables/
cp -r ./speakql-vldb-2022/UIST-2023/tables/* ./tables/
cp -r ./speakql-vldb-2022/UIST-2023/figures/* ./figures/
cp -r ./schemas-for-nl-paper/figures/* ./figures/
cp -r ./schemas-for-nl-paper/tables/* ./tables/

cp ./speakql-vldb-2022/UIST-2023/main-anon.bib ./speakql-ref.bib
cp ./schemas-for-nl-paper/main.bib ./snails-ref.bib
cp ./skalpel-paper/schema-knowledge-focus.bib ./skalpel-ref.bib