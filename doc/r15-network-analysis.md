# Gitcoin Data First Iteration Analysis

We pulled grant, bounty, and hackathon data from Gitcoin, created a relational database schema, and stored the data. We did initial network analysis using NetworkX which led us to shift our priorities for the next iteration. We will investigate regression and clustering on GitHub data selected using the Gitcoin data.

Network density measures showed a strongly connected subnetwork in the Gitcoin data that was based on trivial bounties like Proof of Attendance Protocal bounties for attending a video lecture. Connections based on such bounties are limited in their ability to show significant similarity between the participants. Removing that subnetwork left us with a very sparse network that holds some promise for future work, but is a bit thin for getting traction quickly.

GitHub data includes project participation, commits, bug reports, project creation, and other substantial measures of a person's productive work. We will start with a multi-label classifier to provide an embedding that expresses the meaning of a commit. This will be the first foundation block for a transfer learning model that will combine embeddings for key behaviors on GitHub to build a model of a person that expresses the dimensions of their work history.

## Network Analysis

For our investigation of Gitcoin bounties, we pulled data on 8,858 bounties and 11,688 hackers. We stored the data in a relational database (see img 3.9.2 below) and pulled it into [NetworkX](https://networkx.org/) for analysis. Many nodes were isolated or nearly isolated and were excluded in the model. We found two distinct subnetworks in the remaining data.

The denser network was clustered around bounty nodes that had "POAP" ([Proof Of Attendance Protocol](https://beincrypto.com/learn/poap-proof-of-attendance-protocol/)) in the name. A second, much sparser, network remained after removing those densely connected nodes. We looked at the network of bounty nodes for POAP and non-POAP bounties, then at the network of hackers who worked on non-POAP bounties.

| | **Num Nodes** | **Density** | **Assortativity** | **Notes** |
|------|------:|------:|------:|------|
| POAP Bounty Network | 47 | 0.917 | 0.999 | High and uniform density. |
| Non-POAP Bounty Network | 972 | 0.006 | -0.309 | Low and extremely varied density. |
| Non-POAP Hacker Network | 3,144 | 0.015 | 0.391 | Low and moderately varied density. |

The POAP subnetwork is dense but the edges have very little meaning. Little effort is required to receive a POAP token, so receiving one expresses little about the recipient as a builder. The non-POAP subnetwork has more meaningful edges, but is very sparsely connected. There is not enough data to make strong predictions about the fitness of a hacker to a project.

The Gitcoin network data will help in directing ongoing research, but is not dense enough to work as a primary source at this stage.

## Gitcoin ERD

![Gitcoin ERD](https://github.com/Deadman-DAO/Web3HackerNetwork/blob/main/doc/deadmandao-gitcoin-erd-0.0.4.png "Gitcoin ERD")
