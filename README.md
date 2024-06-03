# statechecker-server
Check if your created tools and websites are running correctly and send a telegram message if not.

## Table of contents
1. [Included packages](#included-packages)
2. [Prerequisites](#prerequisites)
   - [Swarm Cronjobs](#swarm-cronjobs)
   - [If on a multiple master swarm](#if-on-a-swarm-cluster-with-multiple-masters)
     - [Option1: Glusterfs or any other distributed, arbitrarily scalable file system like Ceph (recommended)](#option1-glusterfs-or-any-other-distributed-arbitrarily-scalable-file-system-like-ceph-recommended)
     - [Option2: Constrain deployment to a specific node](#option2-constrain-deployment-to-a-specific-node)
   - [Optional: Traefik (recommended)](#optional-traefik-recommended)
3. [First Setup](#first-setup)
   - [Optional: Telegram status messages](#optional-telegram-status-messages)
   - [Optional: Autoscaler State Checker](#optional-autoscaler-state-checker)
4. [Deploy](#deploy)
5. [Usage](#usage)
   - [AutoScaler](#autoscaler)
     - [Quick overview of labels](#autoscaler)
     - [Detailed information of labels](#full-explanation)
     - [Check Logs](#logs)
   - [Grafana](#grafana)
     - [View Autoscaler Metrics](#view-autoscaler-metrics)
     - [Dashboards](#dashboards)


# Included Packages
- statechecker-db 
  - Database to store statecheck items
- statechecker-api
  - An api to allow usage from clients to send alive-messages: https://github.com/Sokrates1989/statechecker-client.git
- statechecker-check 
  - Periodical check of websites, tools and backups


# Prerequisites
## Swarm Cronjobs?
To make statechecker check run every x minutes (can be customized in .env) deploy https://github.com/crazy-max/swarm-cronjob or another way to implement peridical launch of services.

Implementation help can be found at https://github.com/Sokrates1989/swarm-cronjob.git.

More infromation
 - https://crazymax.dev/swarm-cronjob/
 - https://pkg.go.dev/github.com/robfig/cron#hdr-CRON_Expression_Format
