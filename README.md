# Statistical analysis for patient's records

This series of notebooks provide a collection of algorithms that facilitate an end user to leverage from the already processed data.

## Basic operation
*Neonatal Maternal Hospital's* patient records software outputs several kind of data in various formats. Specifically for this project I choose for it to be `.cvs` files, in order to be able to work easily with `pandas` and `dataframes`.

It has three main modules:
* Emergency
* Hospitalization
* Ambulatory

For each module, treatment is very similar, though it differs in some sutil details. Roughly the analysis made can be summed up as follows:
* **preprocess** - 'cleans' and formats original `.csv`  after converting it in a pandas dataframe, in order to be processed later on
* **concatenate** - allows to 'merge' serveral `.csv` files, in case output is monthly and a year anlaysis is required.
* **medical care** - number of incomes by patient, responding to various criteria:
  * total
  * by hour of the day
  * by day of the week
  * by age group
* **top 20 professionals with most interventions**
* **top 20 most coded diagnostics**
* **reason for discharge**
* **length of stay** - averages in patients length of stay

> **Note:** for discretion reasons, all content in the `.cvs` files has been modified to fulfil this notebook showcase, and preserve patients data confidentiality.

## Streamlit implementation
Lastly, this series of algorithms was bulked in a website leveraging python's [streamlit](https://streamlit.io/) library.
