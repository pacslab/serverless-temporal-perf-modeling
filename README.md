# Temporal Performance Modelling of Serverless Computing Platforms

This repository includes all artifacts for our paper "Temporal Performance Modelling of Serverless Computing Platforms" presented in the [Sixth International Workshop on Serverless Computing (WoSC6) 2020
](https://www.serverlesscomputing.org/wosc6/). The performance model presented in our work is capable of predicting several key performance indicators of serverless computing platforms, while maintaining fidelity and tractabality thoughout the parameter space.

## Benefits

- Works with any service time distribution (general distribution).
- Predicts transient characteristics, making it a proper candidate for use in serverless computing management systems.
- Is tractable while having a high fidelity.

## Artifacts

- [Deployment code for collecting data using experimentations](https://github.com/pacslab/serverless-performance-modeling/tree/master/deployments)
- [Code for parsing the datasets and generating plots](./parsing-experiment-transient.ipynb)

## Requirements

- Python 3.6+
- PIP

## Installation

```sh
pip install -r requirements.txt
```

## License

Unless otherwise specified:

MIT (c) 2020 Nima Mahmoudi & Hamzeh Khazaei

## Citation

You can find the paper with details of the proposed model in [PACS lab website](https://pacs.eecs.yorku.ca/publications/). You can use the following bibtex entry:

```bib
@inproceedings{mahmoudi2020tempperf,
  author={Mahmoudi, Nima and Khazaei, Hamzeh},
  title={{Temporal Performance Modelling of Serverless Computing Platforms}},
  year={2020},
  publisher = {Association for Computing Machinery},
  booktitle={{Proceedings of the 6th International Workshop on Serverless Computing}},
  pages={1--6},
  numpages = {6},
  keywords = {performance modelling, serverless computing, serverless, temporal, transient, performance},
  location = {TU Delft, Netherlands},
  series = {WOSC '20}
}
```

