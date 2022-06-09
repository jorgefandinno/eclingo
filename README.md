# eclingo

> A solver for Epistemic Logic Programs.

![GitHub](https://img.shields.io/github/license/potassco/eclingo?color=blue)
![GitHub release (latest by date)](https://img.shields.io/github/v/release/potassco/eclingo)
![CI badge](https://github.com/jorgefandinno/eclingo/workflows/CI/badge.svg)


---

## Description
`eclingo` is a solver for epistemic logic programs [[1]](#References) built upon the ASP system [`clingo`](https://github.com/potassco/clingo).  
Currently, `eclingo` can compute world views under the following semantics:
- Gelfond 1991; Gelfond and Przymusinska 1993; Gelfond 1994 (G94) [[2, 3, 4]](#References)

## Dependencies

- `python 3.9`
- `clingo 5.5` Python module.

## Installation

### Install clingo

Install the correct version of python and clingo:
```
conda create --name eclingo python=3.9
conda activate eclingo
conda install -c potassco clingo=5.5
```

For installation in development mode go to the [contributing](#Contributing) section below.

### Clone

Clone this repo:
```
git clone https://github.com/potassco/eclingo.git &&
cd eclingo/ &&
git checkout develop
```

### Setup

Change your directory and install `eclingo`:
```
pip install .
```

## Usage


### Input language

`eclingo`'s syntax considers three types of statements:
- [Rules](#rules)
- [Show statements](#show-statements)
- [Constant definitions](#constant-definitions)

#### Rules

`eclingo` accepts rules with the same structure as `clingo` does. Additionally, `eclingo` allows these rules to include subjective literals in their body. These subjective literals are represented using the modal operator **K**, which is represented as `&k{}`. The expression inside the curly braces can be an explicit literal (that is, an atom `A` or its explicit negation `-A`) possibly preceded by default negation, that is represented `not` (alternatively default negation can be represented as `~` for backward compatibility).

> Modal operator **M** is not directly supported but `M q` can be replaced by the construction `not &k{ not q }`.

For example, the epistemic logic program:
```
p <- M q.
```
is written under `eclingo`'s syntax as:
```
p :- not &k{ not q }.
```

#### Show statements
Show statements follow `clingo`'s syntax but, in eclingo, they refer to *subjective atoms*.

For example, the show statement:
```
#show p/1.
```
refers to the subjective atom `&k{p/1}`.

## Contributing

Install clingo using conda as explained [above](#Install-clingo).

Clone this repo (or make your own fork of ```https://github.com/potassco/eclingo.git```):
```
git clone git@github.com:jorgefandinno/eclingo.git &&
cd eclingo &&
git checkout develop
```
Unistall eclingo if you have already installed it
```
pip uninstall eclingo
```
Install eclingo in development model and reactivate conda
```
pip install -e .[dev] &&
conda deactivate &&
conda activate eclingo
```

Test your installation
```
pytest
```
<!-- mypy eclingo -->

To contribute create a new branch
```
git checkout -b <your_name>/<branch>
```
where ```<your_name>``` is to be replaced by your name and ```<branch>``` should be the name of the branch you are creating.

Once you have made the contributions, test that everythink works correctly, commit and push the changes to your branch in the repository.
```
pytest
git commit -am"<comment>"
git push
```
where `<comment>` should state the changes made. If comments are too long to state in one line, you can use ```git commit``` and write them in the editor.

Create a pull request in github.

## License

- **[MIT license](https://github.com/potassco/eclingo/blob/master/LICENSE)**

---

## References

[1] Cabalar P., Fandinno J., Garea J., Romero J. and Schaub T. 2020. eclingo: A solver for Epistemic Logic Programs. In Theory and Practice of Logic Programming.

[2] Gelfond, M. 1991. Strong introspection. In Proceedings of the Ninth National Conference on Artificial Intelligence (AAAI’91), T. Dean and K. McKeown, Eds. AAAI Press / The MIT Press, 386–391.

[3] Gelfond, M. and Przymusinska, H. 1993. Reasoning on open domains. In Logic Programming and Non-monotonic Reasoning, Proceedings of the Second International Workshop, Lisbon, Portugal, June 1993, L. Moniz Pereira and A. Nerode, Eds. MIT Press, 397–413.

[4] Gelfond, M. 1994. Logic programming and reasoning with incomplete information. Annals of Mathematics and Artificial Intelligence 12, 1-2, 89–116.
