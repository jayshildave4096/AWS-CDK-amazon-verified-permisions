permit(
    principal,
    action == MyPolicyStore::Action::"ReadPhotos",
    resource == ?resource
)
when {
    true
};
