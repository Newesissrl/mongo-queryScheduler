# Welcome to the MONGO Query Scheduler Project!

<!-- Mission Statement -->
<!-- More information about crafting your mission statement with examples -->
<!-- https://contribute.cncf.io/maintainers/governance/charter/ -->

MONGO Query Scheduler is a utility service that allows to run custom MongoDB queries and save the output in JSON format.
It can be run directly as a Docker Container or installed via HELM on a Kubernetes cluster as a cronjob to create a recurrent scheduled run, it also gives the possiblity to upload to a GCP bucket for retention.

Possible use cases:
* Run a query and save output on a remote MongoDB isntance without having to use a GUI/shell and/or connect to the server to manipulate output files
* Schedule runs to retrieve data on a regular base (e.g Daily Reports)

The solution has been designed to allow to customize the build in order to better fit different use cases and to allow to schedule multiple different queries, both in docket and k8s


## Getting Started

### For Docker Usage:
under `/app/queries` you can copy your own predefined queries in Python format, the `pipeline` file is the default one which is read at execution if no other filename is passed through env variable.
In this moment the pipeline file contain a basic aggregation query which counts the number of documents and sort them in ascending order.
There are also other two example pipeline which can be used on the MongoDB Atlas Sample Dataset, which is available also on the free tier. They are `movies` and `restaurants`, respectively usable for collection `movies` on db `sample_mflix` and on collection `restaurants` on db `sample_restaurants`.

To create the container image run:
```sh
docker build . -f dockerfiles/dockerfile-mongo-query-executor -t mongo-query-executor:0.0.1
```
To start your container you need three basic informations:
| Variable | Description |
| ------ | ------ |
|MONGO_CONNECTION_STRING | the connection string to your existent MongoDB installation and the DB you want to use |
|MONGO_COLLECTION | The collection where your data are stored |
|USE_PIPELINE_FROM | If you want to use a local pipeline or pass it via variable, possible values are `file` and `env`. If you choose `file` and not pass any specific |filename, default `pipeline` file will be used. |

then run the following command:
```sh
docker run -e MONGO_CONNECTION_STRING="mongodb+srv://<username>:<password>@cluster0.YOUR_CLUSER.mongodb.net/YOUR_DB?retryWrites=true&w=majority" -e MONGO_COLLECTION="YOUR_COLLECTION" -e USE_PIPELINE_FROM="file"”" mongo-query-executor:0.0.1
```
This will create a local file `/app/result_YOUR_COLLECTION_YY-MM-DD-HH-MM-SS.json` with the number of documents sorted in ascending order.


Other Variable available for Docker execution are

| Variable | Description |
| ------ | ------ |
| PIPELINE_QUERY | When you set to `env` the variable `USE_PIPELINE_FROM` you can pass here your custom pipeline in Python format |
| PIPELINE_FILENAME | If you included in your docker build custom defined queries under `/app/queries` folder you can specify the one to be used |
| OVERRIDE_NAME | set a custom name to chart and output file: useful fom different queries from the same collection, otherwise the `MONGO_COLLECTION` value is used |
| GCP_BUCKET_NAME | the GCP bucket name to upload data |
| GCP_BUCKET_FOLDER | The specific subfolder to upload to |

An example for an execution which runs the `movies` pipeline from file on a remote Atlas instance is:
```sh
docker run -e MONGO_COLLECTION="wcm.Stories"  -e MONGO_DB_CONNECTION_STRING="mongodb+srv://test_user:PASSWORD@cluster0.CLUSTER.mongodb.net/sample_mflix?retryWrites=true&w=majority" -e USE_PIPELINE_FROM=“file” -e PIPELINE_FILENAME="movies" mongoquery:0.0.1
```
An example for an execution which runs the `movies` pipeline from env variable on a remote Atlas instance is:
```sh
docker run -e MONGO_COLLECTION="wcm.Stories"  -e MONGO_DB_CONNECTION_STRING="mongodb+srv://test_user:PASSWORD@cluster0.CLUSTER.mongodb.net/sample_mflix?retryWrites=true&w=majority" -e USE_PIPELINE_FROM=“env” -e PIPELINE_QUERY="[ { '$unwind': '$genres' }, { '$group': { '_id': '$genres', 'count': { '$sum': 1 } } }, { '$sort': { 'count': -1 } } ]" mongoquery:0.0.1
```
### For K8S Usage with Helm:

The list of needed values to run the installation of the Mongo Query Scheduler Helm chart is the following one

| Variable | Description |
| ------ | ------ |
| tenant (required) | a unique identifier for the project you are working on |
| environment (required) | a unique identifier for the environment you are working on |
| schedule (required) |  the scheduled toime for your cron execution|
| image_tag (required) | the url of your docker registry where to find the image |
| MongoDbConnectionString (required) |  the connection string to your existent MongoDB installation and the DB you want to use |
| mongodbCollection (required) | The collection where your data are stored |
| usePipelineFrom (required) | If you want to use a local pipeline or pass it via variable, possible values are `file` and `env`. If you choose `file` and not pass any specific filename, default `pipeline` file will be used (filled with the same data of the `env`) |
| suspend  | If set to "true" it stops the execution of the cronjob. Default Value is "false" |
| overrideName | set a custom name to chart and output file: useful fom different queries from the same collection, otherwise the `mongodbCollection` value is used |
| pipelineFilename | If you included in your docker build custom defined queries under `/app/queries` folder you can specify the one to be used |
| gcpBucketName | the GCP bucket name to upload data |
| gcpBucketFolder | The specific subfolder to upload to |

Inside the repository there are already two example values file which can be used on the same MongoDB Atlas Sample Dataset, available also on the free tier. They are `value_movies.yaml` and `values_restaurants.yaml`, respectively usable for collection `movies` on db `sample_mflix` and on collection `restaurants` on db `sample_restaurants`.

To install them inside an existing K8S cluster you just have to add the specific information required for your setup in the values files, navigate the folder and run the following HELM command (the name of the release can be any relevant one for you):

```sh
helm upgrade --install my-awesome-movie-report . -f values_movies.yaml -n my-namespace
```

```sh
helm upgrade --install my-awesome-restaurant-report . -f values_restaurants.yaml -n my-namespace
```

## Contributing

Our project welcomes contributions from any member of our community. To get
started contributing, please see our [Contributor Guide](CONTRIBUTING.md).

## Scope


### In Scope

MONGO Query Scheduler is intended to ease the extraction of data on a regular base from MongoDB instance. It can be run as a docker container or as a cronjob inside K8s to adapt to different scenario. As such, the project has implemented:

* Connection to existing MongoDB instance both on premises on cloud and execute query in standard Python format
* Saving of data on file in JSON format including a standard date format to ease output retention (Format YY-MM-DD-HH-MM-SS)
* The possibility to automatically upload the output file on a GCP bucket
* The possibility to save and recall queries directly inside the image or pass them at execution level
* The possibility to define a cron rotation and eventually suspend it without the need to disinstall

In addition to that other features are actually under development:
* Adding different type of external repository for files (such AWS, Azure, external volumes)
* For the HELM chart the possibility to define several queries in the same configmap and map them dinamically as volumes
* The possibility to export data in CSV by passing custom Python function to map data


### Out of Scope

MONGO Scheduler is not intended to migrate and/or sync data between instances, but to ease the extraction of data on regular base. The following specific functionality will therefore not be incorporated:

* Data Migration between MongoDB instances
* Data import to MongoDB instances


## License

This project is licensed under the [Apache license](LICENSE)

## Conduct

We follow the [CNCF Code of Conduct](CODE_OF_CONDUCT.md).

