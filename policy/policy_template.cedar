permit(
    principal == ?principal,
    action in [ MyPolicyStore::Action::"ReadPhotos", MyPolicyStore::Action::"CreatePhoto" ], 
    resource == ?resource
)
when {
    true
};