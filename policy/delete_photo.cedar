permit(
    principal,
    action == MyPolicyStore::Action::"DeletePhoto", 
    resource
)
when {
    resource.root_user == principal ||
    principal in MyPolicyStore::UserGroup::"admin"
};