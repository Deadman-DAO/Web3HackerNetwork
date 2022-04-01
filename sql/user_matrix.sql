create index bounty_pkx on gitcoin_raw.activity (bounty_pk);

create table gitcoin_matrices.user_pairs as
  select distinct l.profileId left_profileId,
                  l.bounty_pk,
                  r.profileId right_profileId
  from gitcoin_raw.activity l
  join gitcoin_raw.activity r on r.bounty_pk = l.bounty_pk
                  and r.profileId > l.profileId
;

create table gitcoin_matrices.user_sparse_matrix as
select left_profileId,
       right_profileId,
       count(1) as weight
from gitcoin_matrices.user_pairs
group by left_profileId, right_profileId
;

create table gitcoin_matrices.user_square_matrix as
select left_profileId as profile_id,
       weight,
       right_profileId as other_profile_id
from gitcoin_matrices.user_sparse_matrix
union
select right_profileId as profile_id,
       weight,
       left_profileId as other_profile_id
from gitcoin_matrices.user_sparse_matrix
;

select count(distinct profile_id)
from gitcoin_matrices.user_square_matrix
where weight > 2
;


-- ---------------------------------------------
create table gitcoin_matrices.paid_pairs as
  select distinct l.profileId left_profileId,
                  l.bounty_pk,
                  r.profileId right_profileId
  from gitcoin_raw.activity l
  join gitcoin_raw.activity r on r.bounty_pk = l.bounty_pk
                  and r.profileId > l.profileId
  where l.activity_type = 'worker_paid'
  and r.activity_type = 'worker_paid'
;
create index lpidx on gitcoin_matrices.paid_pairs(left_profileId);
create index rpidx on gitcoin_matrices.paid_pairs(right_profileId);

create table gitcoin_matrices.submit_pairs as
  select distinct l.profileId left_profileId,
                  l.bounty_pk,
                  r.profileId right_profileId
  from gitcoin_raw.activity l
  join gitcoin_raw.activity r on r.bounty_pk = l.bounty_pk
                  and r.profileId > l.profileId
  where l.activity_type = 'work_submitted'
  and r.activity_type = 'work_submitted'
;
create index lpidx on gitcoin_matrices.submit_pairs(left_profileId);
create index rpidx on gitcoin_matrices.submit_pairs(right_profileId);

create table gitcoin_matrices.paid_submit_pairs as
  select s.left_profileId, s.bounty_pk, s.right_profileId
  from gitcoin_matrices.submit_pairs s
  join gitcoin_raw.activity l_paid on l_paid.profileId = s.left_profileId
  join gitcoin_raw.activity r_paid on r_paid.profileId = s.right_profileId
  where l_paid.activity_type = 'worker_paid'
  and r_paid.activity_type = 'worker_paid'
;
create index lpidx on gitcoin_matrices.paid_submit_pairs(left_profileId);
create index rpidx on gitcoin_matrices.paid_submit_pairs(right_profileId);

create table gitcoin_matrices.paid_submit_user_sparse_matrix as
select left_profileId,
       right_profileId,
       count(1) as weight
from gitcoin_matrices.paid_submit_pairs
group by left_profileId, right_profileId
;


-- ============= Fulfillment Based User/User ===========

create table gitcoin_matrices.user_fulfillment_pairs as
  select distinct l.profileID as left_profile_id,
                  l.bountyPK as bounty_pk,
                  r.profileID as right_profile_id
  from gitcoin_raw.fulfillment l
  join gitcoin_raw.fulfillment r on r.bountyPK = l.bountyPK
                  and r.profileID > l.profileID
;
create index lpidx on gitcoin_matrices.user_fulfillment_pairs(left_profile_id);
create index rpidx on gitcoin_matrices.user_fulfillment_pairs(right_profile_id);


create table gitcoin_matrices.user_non_poap_fulfill_pairs as
  select distinct l.profileID as left_profile_id,
                  l.bountyPK as bounty_pk,
                  r.profileID as right_profile_id
  from gitcoin_raw.fulfillment l
  join gitcoin_raw.fulfillment r on r.bountyPK = l.bountyPK
                  and r.profileID > l.profileID
  where not exists ( select 1 from poap_like p where p.pk = l.bountyPK )
  and not exists ( select 1 from poap_like p where p.pk = r.bountyPK )
;
create index lpidx on gitcoin_matrices.user_non_poap_fulfill_pairs(left_profile_id);
create index rpidx on gitcoin_matrices.user_non_poap_fulfill_pairs(right_profile_id);

create table gitcoin_matrices.user_non_poap_matrix as
select left_profile_id,
       right_profile_id,
       count(1) as weight
from gitcoin_matrices.user_non_poap_fulfill_pairs
group by left_profile_id, right_profile_id
;
create index unpm_lidx on user_non_poap_matrix (left_profile_id);
create index unpm_ridx on user_non_poap_matrix (right_profile_id);

create table gitcoin_matrices.user_non_poap_bi_matrix as
select left_profile_id as profile_id,
       weight,
       right_profile_id as other_profile_id
from gitcoin_matrices.user_non_poap_matrix
union
select right_profile_id as profile_id,
       weight,
       left_profile_id as other_profile_id
from gitcoin_matrices.user_non_poap_matrix
;
create index unpbm_idx on user_non_poap_bi_matrix (profile_id);
create index unpbm_oidx on user_non_poap_bi_matrix (other_profile_id);

