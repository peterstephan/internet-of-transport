*****
OVERVIEW
*****

The Internet of Transport (IoT) aims to provide a toolkit for analysts, data scientists, modellers and developers from the public and private sectors in the transport and mobility industry to (1) gather data from sources on the web, (2) store it in the cloud, and (3) produce insights through visualisation, analytics, alerts and messaging etc.

*****
DOCUMENTATION
*****
This documentation is available on ReadTheDocs.org at:

`https://internet-of-transport.readthedocs.io <https://internet-of-transport.readthedocs.io>`_


*****
ARCHITECTURAL CHOICES
*****

ARCHITECTUAL OVERVIEW
########

- **Amazon Web Services (AWS)** has been selected as the **cloud platform** (see below for further discussion)
- To be confirmed through usage and evaluation; however **serverless** cloud products (e.g. AWS Lambdas) are preferred as they are simpler to setup and maintain, which makes them more accessible to analysts and users who are more interested in the outputs of the data and analysis than the way of getting there
- Scripting/code: **Python** is the preferred programming language due to its popularity and strengths in data analysis. **R** may also be investigated and used as well, particularly the **R Shiny** package for visualisation and ease of hosting on **ShinyApps.io**
- Data Storage: **PostgreSQL** is the preferred database due to its popularity, its open-source and its **PostGIS** extension. **AWS S3 Buckets** are also preferred for bucket-type file storage, with **CSV** files preferred (although JSON, GeoJSON, compressed zipped and spatial formats may also be used at time). NoSQL databases may also be investigated.  
- Visualisation: a combination of open-source and commonly-used commercial products will be used including **Tableau** (particularly as its allows data visualisations to be shared for free for this project using Tableau Public), as well as PowerBI, QGIS for GIS software, Leaflet.jt, D3.js, Python and R / R Shiny.


CLOUD PLATFORM - AWS
########

Amazon Web Services (AWS) has been selected as the primary cloud platform to develop on and utilise. The primary reasons for this are that: 
(a) in general, it is often considered the market leading product^^ at the start of this project; and
(b) in the transport sector, it also anecdotally the most used currently


^^Some further reading on AWS vs Microsoft Azure vs Google Cloud is available here:
'https://medium.com/@distillerytech/comparing-aws-vs-azure-vs-google-cloud-platforms-for-enterprise-app-development-28ccf827381e <https://medium.com/@distillerytech/comparing-aws-vs-azure-vs-google-cloud-platforms-for-enterprise-app-development-28ccf827381e>`_

*****
EXAMPLE APPLICATIONS
*****

#1. Real-Time Google Maps Travel Time Data Gathering & Visualisation
########

More info coming soon...


#2. Real-Time VicRoads API Bluetooth Link Data Gathering & Visualisation
########

More info coming soon...
