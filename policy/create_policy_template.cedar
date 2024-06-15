permit(
    principal,
    action == MyPolicyStore::Action::"CreatePhoto",
    resource == ?resource
)
when {
    principal in MyPolicyStore::UserGroup::"creator"
};
