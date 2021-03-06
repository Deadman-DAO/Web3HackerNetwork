# Part 1 - Proposal

## Name of Project: *DeadmanDAO Web3 Hacker Network*

## Proposal in one sentence

Create a decentralized data science system to help hackers, teams, and projects to find each other.

## Description of the project and what problem it is solving

Finding Web3 developers to work with on bounties, hackathons, and grants is challenging. You can go to Discord and post, but your reach will be limited. You can search on LinkedIn, but that data is often stale or aspirational. Web3 Hacker Network will provide analytics about the network of people who are building Web3.

It can be challenging to scale a team for a project without the costly HR departments used to grow engineering departments in Web2. DeadmanDAO is beginning down the road toward facilitating decentralized talent mobility.

## Grant Deliverables

* Raw dataset from GitHub with data regarding some initial Web3 projects for analysis.
* Metrics from the cloned repository for each of the initial projects regarding commits, committers, and file types.
* Data exploration showing potential features for inclusion in an initial multi-label classification model for commits.
* Initial manual labeling of some example commits.
* Baseline F1 score for a simple regression model.
* Analysis of the dataset and model to assess fitness to task and gaps to be filled.
* Publish a dataset on Ocean Market with commit history embeddings for an initial test set of hackers.

## Project Category: *Unleash Data*

## Earmark: *New Project*

## What is the final product?

Web3 Hacker Network is a data science system incorporating network, regression, clustering, and classification models to increase tech talent mobility in Web3. The final product is a decentralized autonomous opportunity discovery engine for hackers, backers, projects, and teams. It will provide some of the services of hiring managers and HR departments from Web2, but in a fashion that is more aligned with the decentralized and self-service nature of Web3.

Web2 notions of long employment with a single firm are breaking down. In Web3 hackers are working across more projects for shorter periods of time, resulting in greater innovation through increased cross-pollination of ideas. Opportunity discovery and resource placement in this more dynamic environment will have to move faster and cost less than Web2 HR-driven hiring pipelines.

Network theory, machine learning, and the open data about work history in Web3 allows for automated opportunity discovery. Web3 Hacker Network is breaking ground on a long-term project that will serve hackers, backers, projects, and teams. The final product will present users with a menu of opportunities that match their role in the ecosystem and preferences for developing their professional life.

## Which value add criteria are we focusing on? Why do we believe we will do well?

### option 1: Usage of Ocean
- how well might the project drive usage of Ocean. Measure with e.g. Data Consume Volume, # assets published, TVL (total value locked), Network Revenue, # active users, # funded projects.

Network Revenue: Our first iteration focused on Gitcoin data, we are now adding GitHub data. Gitcoin grants and bounties have totalled more than $10m in the past 12 months, with a steady baseline around $500k/month. For many years GitHub has been the center of orders of magnitude more value creation across Web2 and Web3. Our dataset and compute will have an influence on total productivity in the millions to tens of millions per month.

The value of improved talent mobility can be estimated by headhunter service fees, which range from 20 - 25%. Our automated system will not provide all the services of HR departments or headhunters, but it will act more objectively. If it provides one quarter of the value of a headhunter, that suggests it will improve productivity by 5% of millions to tens of millions. That puts it in the vicinity of $500k per month of value creation.

Gitcoin provides core data on active hackers in Web3, GitHub will add more data about their work history and expose more information about early and potential Web3 hackers. The road ahead includes adding data from blockchain analytics providers and grant funders like MolochDAO, Harmony, and Genesis DAO.

And this is only the beginning. We expect Web3 to surpass Web2 in the long run, and for dynamic team composition to be the new normal. There will be hundreds of millions of dollars worth of human resource assignments happening every month. Tools like this one will be responsible for millions of dollars in increased talent placement efficiency per month.

### option 2: Viability
- what is the chance of success of the project

Our data engineering and data science person built Spark-based DE and ML systems at Amazon on terabyte datasets, then managed a team doing the same through several deliveries on time and on budget. Our React engineer designed and delivered US DoD warehouse automation systems on strict timelines and budgets.

Over the coming months and iterations we will need to expand the team to deliver the larger vision. Our lead grew a team at Amazon from 3 people to 12 people in one year while delivering on an aggressive project schedule. His ability to find the right people, build team spirit, and motivate enthusiastic engagement were the core of his success.

There is always risk, and this is a highly exploratory project. Nothing is guaranteed, but our core team is strong and the data we need is available.

### option 3: Community engagement
- how active is the team in the community?

### option 4: Adding value to the overall community
- how well does the outcome of the project add value to the Ocean community / ecosystem

The long-term project will be integral to the work cycle of a significant portion of Web3 producers. This product will expose a large number of active Web3 hackers and team builders to Ocean Protocol.

## Funding Requested: *$3000*

## Proposal Wallet Address: *0xAE6A3d5F73cDA0180eeDBAa5aA801D68b3491931*

## Have you previously received an OceanDAO Grant?: *No*

## Team Website: [www.DeadmanDAO.com](https://www.deadmandao.com/)

## Discord Handle: *DeadmanBob#7342*

## Project lead full name: *Robert Bushman*

## Project lead email: *oceanprotocol at traxel dot com*

## Country of Residence: United States of America

# Part 2 - Team

## 2.1 Core Team

### Robert Bushman

* Role: Project Manager, Developer
* Relevant Credentials:
    * LinkedIn: https://www.linkedin.com/in/robert-bushman-9316412/
    * GitCoin: https://gitcoin.co/rbb36
    * GitHub: https://github.com/rbb36
* Background / Experience:
    * L6 SDE / L6 SDM at Amazon (data engineering & data science)
    * Big Data Architect at Choice Hotels
    * Senior Software Engineer at Apple
    * Successful first Bounty attempt (rbb36)
        * Bounty Submission: https://gitcoin.co/hackathon/schellingpoint/projects/13517/new2web3/summary?
        * Victory Transaction: https://etherscan.io/tx/0x191ca45381225eff6693b04ddb720d43f62d2006d14e0f345ac1dd8b77c58f06

### Matt Enke

* Role: Developer
* Relevant Credentials
    * LinkedIn: https://www.linkedin.com/in/matt-enke-b234ba51/
    * GitCoin: https://gitcoin.co/enigmatt
    * GitHub: https://github.com/enigmatt
* Background / Experience
    * System Architect and Engineer: US DoD Warehouse Automation
    * Successful first Bounty attempt (enigmatt)
        * Bounty Submission: https://gitcoin.co/hackathon/schellingpoint/projects/13517/new2web3/summary?
        * Victory Transaction: https://etherscan.io/tx/0x191ca45381225eff6693b04ddb720d43f62d2006d14e0f345ac1dd8b77c58f06

# Part 3 - Proposal Details [revision TBD]

## 3.1 Details

We propose extending our data pipeline to include GitHub data in addition to our existing Gitcoin data, and to publish an example dataset of commit classifications on Ocean Market. To produce that dataset, we will do an initial iteration on feature and target engineering toward clustering and regression models. Two engineers will be involved during this iteration. Future iterations will expand the project based on discovery, demand, feedback, and developer engagement.

## 3.2 and 3.3 intentionally removed

## 3.4 Which Ocean-powered data market will data be published on?

Initial deployment will be on Ocean Market. In subsequent rounds we will explore the RoI of forking our own market. We have system administration experience; if and when we deploy our own market is a question of when the value exceeds the value of competing priorities.

## 3.4 through 3.8 intentionally removed

## 3.9 Project Deliverables - Roadmap

### Any prior work completed thus far? Details?

We pulled grant, bounty, and hackathon data from Gitcoin, created a relational database schema, and stored the data. We did initial network analysis using NetworkX which led us to shift our priorities for the next iteration. We will investigate regression and clustering on GitHub data selected using the Gitcoin data.

Network density measures showed a strongly connected subnetwork in the Gitcoin data that was based on trivial bounties like Proof of Attendance Protocal bounties for attending a video lecture. Connections based on such bounties are limited in their ability to show significant similarity between the participants. Removing that subnetwork left us with a very sparse network that holds some promise for future work, but is a bit thin for getting traction quickly.

GitHub data includes project participation, commits, bug reports, project creation, and other substantial measures of a person's productive work. We will start with a multi-label classifier to provide an embedding that expresses the meaning of a commit. This will be the first foundation block for a transfer learning model that will combine embeddings for key behaviors on GitHub to build a model of a person that expresses the dimensions of their work history.

#### 3.9.1: Network Analysis

For our investigation of Gitcoin bounties, we pulled data on 8,858 bounties and 11,688 hackers. We stored the data in a relational database (see img 3.9.2 below) and pulled it into [NetworkX](https://networkx.org/) for analysis. Many nodes were isolated or nearly isolated and were excluded in the model. We found two distinct subnetworks in the remaining data.

The denser network was clustered around bounty nodes that had "POAP" ([Proof Of Attendance Protocol](https://beincrypto.com/learn/poap-proof-of-attendance-protocol/)) in the name. A second, much sparser, network remained after removing those densely connected nodes. We looked at the network of bounty nodes for POAP and non-POAP bounties, then at the network of hackers who worked on non-POAP bounties.

| | **Num Nodes** | **Density** | **Assortativity** | **Notes** |
|------|------:|------:|------:|------|
| POAP Bounty Network | 47 | 0.917 | 0.999 | High and uniform density. |
| Non-POAP Bounty Network | 972 | 0.006 | -0.309 | Low and extremely varied density. |
| Non-POAP Hacker Network | 3,144 | 0.015 | 0.391 | Low and moderately varied density. |

The POAP subnetwork is dense but the edges have very little meaning. Little effort is required to receive a POAP token, so receiving one expresses little about the recipient as a builder. The non-POAP subnetwork has more meaningful edges, but is very sparsely connected. There is not enough data to make strong predictions about the fitness of a hacker to a project.

The Gitcoin network data will help in directing ongoing research, but is not dense enough to work as a primary source at this stage.

#### 3.9.2: Gitcoin ERD

![Gitcoin ERD](https://github.com/Deadman-DAO/Web3HackerNetwork/blob/main/doc/deadmandao-gitcoin-erd-0.0.4.png "Gitcoin ERD")

### What is the project roadmap?

1. Milestone 1 (End of Week 1): GitHub API connection. Initial dataset calls. Document potential features and targets for regression model.
1. Milestone 2 (End of Week 2): Clone target repositories. Begin commit feature engineering.
1. Milestone 3 (End of Week 3): Data analytics on commit features. Document gaps and adjust as needed.
1. Milestone 4 (End of Week 4): Manual labelling of example commits. Initial attempt at classification.
1. Milestone 5 (End of Week 5): Classifier algorithm comparison. Hyperparameter tuning. Baseline F1 score.
1. Milestone 6 (End of Week 6): Analysis of results so far, fitness to task, and gaps to be filled.
1. Milestone 7 (End of week 7): Publish commit classification dataset on Ocean Market, announce on web page and elsewhere as suits.
1. Milestone 8 (End of week 8): Write the next round Ocean grant proposal.

### What is the team's future plans and intentions?

We intend to continue extending the work as long as we are gaining traction and improving talent mobility.

## 3.10 Additional Information

We submitted a grant proposal to Ocean in Round 15. OCEAN was, along with all cryptocurrencies, reeling from Russia's invasion of Ukraine. There were a few more than usual New Entrant proposals, and they were all quite interesting. The currency limited the number of funded grants to 3.5 and the stiff competition prevented us from securing a grant.

We submitted a grant proposal to Gitcoin at the same time as we submitted for Ocean Round 15. We are new to Web3 and have limited social media histories (for my part, I am a privacy advocate and have intentionally eschewed it). Due to this, we were difficult to distinguish from a Sybil and were denied participation. We have been building up our image to make it more clear that we are actual humans who are actively working on the project. We will submit to Gitcoin again for their next round.

