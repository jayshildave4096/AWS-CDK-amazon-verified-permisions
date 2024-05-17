permit(
    principal,
    action == MyPolicyStore::Action::"DeletePhoto", 
    resource
)
when {
    principal in MyPolicyStore::UserGroup::"admin"
};