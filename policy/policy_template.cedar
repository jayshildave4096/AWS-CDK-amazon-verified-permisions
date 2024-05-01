permit(
    principal == ?principal,
    action in [ MyPolicyStore::Action::"ReadPhotos", MyPolicyStore::Action::"CreatePhoto", MyPolicyStore::Action::"DeletePhoto" ], 
    resource == ?resource
)
when {
    resource.root_user == principal ||
    principal in MyPolicyStore::UserGroup::"admin"
};