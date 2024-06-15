permit(
  principal == MyPolicyStore::User::"test_user",
  action in [MyPolicyStore::Action::"DeletePhoto"],
  resource == MyPolicyStore::Photo::"sunset.jpg"
) when {
  true
};
