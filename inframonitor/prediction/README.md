# Predictor module

* Uses `datascience` module from the `datascience` repository. Do not modify sources here,
modify them in the upstream repo and reimport.
* `datascience.version` contains the commit hash from the import.
* `dbconnector` and `mqttconnector` are reused from the `mqtttodbconnector` module.
* Create models for sensors in the `datascience` repo and copy the pickle files into the
  `model` folder (Adding/modifying models does not require to restart the module)