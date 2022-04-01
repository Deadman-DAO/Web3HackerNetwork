create index profileIdx on gitcoin_raw.activity (profileId);
create index pkx on gitcoin_raw.bounty(pk);

create table gitcoin_matrices.bounty_pairs as
  select distinct l.bounty_pk left_bounty_pk,
                  l.profileId,
                  r.bounty_pk right_bounty_pk
  from gitcoin_raw.activity l
  join gitcoin_raw.activity r on r.profileId = l.profileId
                              and r.bounty_pk > l.bounty_pk
;

create table gitcoin_matrices.bounty_sparse_matrix as
select left_bounty_pk,
       right_bounty_pk,
       count(1) as weight
from gitcoin_matrices.bounty_pairs
group by left_bounty_pk, right_bounty_pk
;
create index lpkx on gitcoin_matrices.bounty_sparse_matrix (left_bounty_pk);
create index rpkx on gitcoin_matrices.bounty_sparse_matrix (right_bounty_pk);

create table gitcoin_matrices.bounty_square_matrix as
select left_bounty_pk as bounty_pk,
       weight,
       right_bounty_pk as other_bounty_pk
from gitcoin_matrices.bounty_sparse_matrix
union
select right_bounty_pk as bounty_pk,
       weight,
       left_bounty_pk as other_bounty_pk
from gitcoin_matrices.bounty_sparse_matrix
;
create index bpkx on gitcoin_matrices.bounty_square_matrix (bounty_pk);
create index obpkx on gitcoin_matrices.bounty_square_matrix (other_bounty_pk);

select count(distinct bounty_pk)
from gitcoin_matrices.bounty_square_matrix
where weight > 2
;

-- ---------------------------------------
select l.title, r.title
from gitcoin_matrices.bounty_sparse_matrix s
join gitcoin_raw.bounty l on l.pk = s.left_bounty_pk
join gitcoin_raw.bounty r on r.pk = s.right_bounty_pk
where s.weight = 18
;

create table gitcoin_matrices.bounty_worked_pairs as
  select distinct l.bounty_pk left_bounty_pk,
                  l.profileId,
                  r.bounty_pk right_bounty_pk
  from gitcoin_raw.activity l
  join gitcoin_raw.activity r on r.profileId = l.profileId
                  and r.bounty_pk > l.bounty_pk
  where l.activity_type = 'work_submitted'
  and r.activity_type = 'work_submitted'
;
create index lpidx on gitcoin_matrices.bounty_worked_pairs(left_profileId);
create index rpidx on gitcoin_matrices.bounty_worked_pairs(right_profileId);

create table gitcoin_matrices.bounty_worked_matrix as
select left_bounty_pk,
       right_bounty_pk,
       count(1) as weight
from gitcoin_matrices.bounty_worked_pairs
group by left_bounty_pk, right_bounty_pk
;
create index lpkx on gitcoin_matrices.bounty_worked_matrix (left_bounty_pk);
create index rpkx on gitcoin_matrices.bounty_worked_matrix (right_bounty_pk);

create table gitcoin_matrices.bounty_worked_bi_matrix as
select left_bounty_pk as bounty_pk,
       weight,
       right_bounty_pk as other_bounty_pk
from gitcoin_matrices.bounty_worked_matrix
union
select right_bounty_pk as bounty_pk,
       weight,
       left_bounty_pk as other_bounty_pk
from gitcoin_matrices.bounty_worked_matrix
;
create index bpkx on gitcoin_matrices.bounty_worked_bi_matrix (bounty_pk);
create index obpkx on gitcoin_matrices.bounty_worked_bi_matrix (other_bounty_pk);


-- =========== Fulfillment Based ================

create table gitcoin_matrices.bounty_fulfillment_pairs as
  select l.bountyPK as left_bounty_pk,
         l.profileID as profile_id,
         r.bountyPK as right_bounty_pk
    from gitcoin_raw.fulfillment l
    join gitcoin_raw.fulfillment r on r.bountyPK > l.bountyPK
                                   and r.profileID = l.profileID
;
create index lpkx
  on gitcoin_matrices.bounty_fulfillment_pairs(left_bounty_pk);
create index rpkx
  on gitcoin_matrices.bounty_fulfillment_pairs(right_bounty_pk);

create table gitcoin_matrices.bounty_fulfillment_matrix as
select left_bounty_pk,
       right_bounty_pk,
       count(1) as weight
from gitcoin_matrices.bounty_fulfillment_pairs
group by left_bounty_pk, right_bounty_pk
;
create index lpkx
  on gitcoin_matrices.bounty_fulfillment_matrix (left_bounty_pk);
create index rpkx
  on gitcoin_matrices.bounty_fulfillment_matrix (right_bounty_pk);

create table gitcoin_matrices.bounty_fulfillment_bi_matrix as
select left_bounty_pk as bounty_pk,
       weight,
       right_bounty_pk as other_bounty_pk
from gitcoin_matrices.bounty_fulfillment_matrix
union
select right_bounty_pk as bounty_pk,
       weight,
       left_bounty_pk as other_bounty_pk
from gitcoin_matrices.bounty_fulfillment_matrix
;
create index bpkx on gitcoin_matrices.bounty_fulfillment_bi_matrix (bounty_pk);
create index obpkx on gitcoin_matrices.bounty_fulfillment_bi_matrix (other_bounty_pk);
