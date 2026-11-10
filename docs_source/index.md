# village-report-generator

Every day, on the cluster, this repository makes an HTML report of each
active project of the [Training Village](https://braincircuitsbehaviorlab.github.io/village/)
and publishes it on the [reports website](https://learningcircuitslab.github.io/village-report-generator/),
with a calendar to choose the day.

A report has an **Overview** tab (corridor plot of the last days, TV report,
trials per training stage, trials and performance of the last days, box
occupancy, performance of the cohort), one tab per **subject** (training
history and the session of the day) and a **Problems** tab listing anything
that could not be drawn. A separate report shows the temperature and humidity
of the room.

The analysis and figures come from
[lecilab-behavior-analysis](https://learningcircuitslab.github.io/lecilab-behavior-analysis/);
this repository only decides what goes in each report, renders it with
[Quarto](https://quarto.org/) and publishes it.

[See an example report](example), made from the sample data by the current
code.

```{toctree}
:maxdepth: 2
:hidden:

how_it_works
configuration
running
example
api_index
```
