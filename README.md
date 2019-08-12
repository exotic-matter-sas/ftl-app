# Paper Matter

Archiving documents solution

## For users

### Requirements

 * Python 3.7
 * PostgreSQL 11
 * Java 8+
 
### Install Python modules
 
    python -m pip install requirements.txt

## For developers

### Requirements

 * Python 3.7
 * PostgreSQL 11
 * Firefox or Chrome (to run functional tests)
 * Poedit or equivalent (to add/update i18n)
 * Node.js LTS
 * Java 8+ (for documents indexing)

 * _Under Linux, you may need additional tools to build Python modules which includes C code:_
   * _apt-get install build-essential python3-dev libpq-dev_

### Install Python modules
 
    python -m pip install requirements.txt
    python -m pip install requirements_dev.txt

### Install Node modules
 
    cd ftl/vuejs-app
    npm install
    
### Run local server

First terminal

    npm run serve

Second terminal
    
    python manage.py runserver

### Tests

#### Python

Run all tests

    python manage.py test --parallel
    # Run all tests excepted slow ones (all functional tests are tagged as "slow")
    python manage.py test --parallel --exclude-tag=slow
    
Run test for a specific module

    python manage.py test ftests # run only functional tests
    python manage.py test core # run unit tests of core module

#### VueJS

Run all tests

    vue-cli-service test:unit
    
_Or alternatively `npx vue-cli-service test:unit`_

### i18n
 
 :warning: _Avoid raw editing of .po files, use poedit or equivalent instead_
 
 Add a new language or create new key to translate in .po files:
 
    python manage.py makemessages -l fr --ignore=requirements*.txt,__init__.py,ftest/*
    # Following lines needed for frontend i18n
    npm run build
    python manage.py makemessages -l fr --ignore=node_modules -d djangojs

 Update existing i18n key in .po files:
 
    python manage.py makemessages --all
    
 Compile .mo files:
 
    python manage.py compilemessages
    
 _note: generated .mo files aren't versioned and should be regenerated locally after each .po files update._
    
### Django settings

To use specific Django settings without modifying main `ftl/ftl/settings.py` file, create a `ftl/ftl/settings_local.py` file and override desired setting in it.

### Build app

#### 1. compile Vuejs files

    npm run build

#### 2. collect static files to an unique dir using Django

    python3 manage.py collectstatic
    
### Reindex all documents

    python manage.py reindex_docs
    
# Credits
 - Programming languages:
   - [Python](https://www.python.org/)
   - [Vue.js](https://vuejs.org/)

 - Main technologies used:
   - Web framework: [Django](https://www.djangoproject.com/)
   - Database: [PostgreSQL](https://www.postgresql.org/)
   - Document storage, [django-storages](https://github.com/jschneier/django-storages) allow to choose between:
     - File system
     - [Google Cloud Storage](https://cloud.google.com/storage/)
     - [Amazon S3](https://aws.amazon.com/s3/)
   - Optical Character Recognition, to choose between:
     - _disable_
     - [Google Cloud Vision API (sync or async)](https://cloud.google.com/vision/docs/)
     - [Amazon Textract API](https://aws.amazon.com/textract/)
   - Document text extraction: [Apache Tika](https://tika.apache.org/)
   - Document preview: [PDF.js](https://mozilla.github.io/pdf.js/)
   - Search engine: [PostgreSQL tsvector](https://www.postgresql.org/docs/10/datatype-textsearch.html)

 - UI:
   - Logo police: [Quicksand](https://github.com/andrew-paglinawan/QuicksandFamily)
   - App Icons: [Font Awesome](https://fontawesome.com/)
   - SVG illustrations: [Undraw](https://undraw.co/)
 