# `solved-af` — Solved Argumentation Framework

## an abstract argumentation framework solver to learn from.

<p align="center">
  <img src="./images/example.png" width="800px" />
</p>

This repository contains the implementation of an argumentation framework solver to be submitted as part of the final year project (Bachelor Thesis) of David Simon Tetruashvili @ King's College London.

`solved-af`...

- ...is SAT-reduction based.

- ...is written in pure Python 3.

- ...supports both inputs formats defined in the ICCMA'19 specification ([TGF](https://www.wikiwand.com/en/Trivial_Graph_Format), and [APX](https://www.dbai.tuwien.ac.at/research/argumentation/aspartix/dung.html)).

- ...is capable of solving all classic track problems under the Dung's four main abstract argumentation semantics.

# Prerequisites

**`solved-af` uses [`glucode-syrup`](https://www.labri.fr/perso/lsimon/glucose/) SAT solver.** `glucode-syrup` has to be installed in the `PATH` for `solved-af` to work out of the box.

It is possible to change the SAT solver command from within the source code via the `SAT_COMMAND` constant variable in `saf/tasks.py` provided that the new solver has similar DIMACS input/output formats.

## Installation

#### Via `install.sh` script

Use the included `install.sh` script to install `solved-af`.

<p align="center">
  <img src="./images/installation-via-script.png" width="800px" />
</p>

```bash
$ git clone https://github.kcl.ac.uk/K1764158/solved-af.git
$ cd solved-af
$ chmod +x ./install.sh && ./install.sh
```

#### Via `pip`

Use the package manager [`pip`](https://pip.pypa.io/en/stable/) to install `solved-af`.

<p align="center">
  <img src="./images/installation-via-pip.png" width="800px" />
</p>

```bash
$ git clone https://github.kcl.ac.uk/K1764158/solved-af.git
$ cd solved-af
$ pip install -e .
```

## Usage

`solved-af` follows the established ICCMA solver interface closely with the added option of switching input validation via the `-v` flag.

<p align="center">
  <img src="./images/usage.png" width="800px" />
</p>

## Extendability

In contrast to other available AF solvers, `solved-af` is meant to be flexible, easy to understand and extend (albeit at the cost of performance). For example, here is how to use a reduction parser (`TheoryParser`) to reduce stable semantics to SAT and subsequently solve the full enumeration (`EE-ST`) task under it.

<p align="center">
  <img src="./images/extendibility.png" width="800px" />
</p>

# Testing scripts

Included in this repository are some scripts used for running `solved-af` on a set of instances and comparing them to a set of reference results. Both of these data sets can be found [here](https://www.iccma2019.dmi.unipg.it/files.html). These scripts rely on `comp-exts-mpz` (O. Rodrigues) and [`runsolver`](https://www.cril.univ-artois.fr/~roussel/runsolver/) which are not included here.

Running `./run-tests.sh` or `./run_decision_tests.sh` without arguments shows usage messages.

The scripts will generate CSV files with the recorded data. They are compatible with any ICCMA interface compatible solver.

## Licence

[GNU GPL v3](https://choosealicense.com/licenses/gpl-3.0/)
