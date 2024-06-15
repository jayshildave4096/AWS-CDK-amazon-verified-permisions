from aws_cdk import Stack, CfnOutput, aws_verifiedpermissions as verifiedpermissions
from constructs import Construct
import json
import os


class AVPStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        with open("schema.json") as file:
            cfn_policy_store = verifiedpermissions.CfnPolicyStore(
                self,
                "MyPolicyStore",
                validation_settings=verifiedpermissions.CfnPolicyStore.ValidationSettingsProperty(
                    mode="STRICT"
                ),
                description="MyPolicyStore",
                schema=verifiedpermissions.CfnPolicyStore.SchemaDefinitionProperty(
                    cedar_json=json.dumps(json.loads(file.read()))
                ),
            )
            os.environ.setdefault(
                "POLICY_STORE_ID", cfn_policy_store.attr_policy_store_id
            )

        with open("./policy/create_policy_template.cedar") as policy_template_file:
            create_photo_policy_template = verifiedpermissions.CfnPolicyTemplate(
                self,
                "CreatePhotoTemplate",
                statement=policy_template_file.read(),
                # the properties below are optional
                policy_store_id=str(cfn_policy_store.attr_policy_store_id),
            )

            cfn_policy = verifiedpermissions.CfnPolicy(
                self,
                "CreatePhotoTemplatePolicy",
                definition=verifiedpermissions.CfnPolicy.PolicyDefinitionProperty(
                    template_linked=verifiedpermissions.CfnPolicy.TemplateLinkedPolicyDefinitionProperty(
                        policy_template_id=str(
                            create_photo_policy_template.attr_policy_template_id
                        ),
                        resource=verifiedpermissions.CfnPolicy.EntityIdentifierProperty(
                            entity_id="sunset.jpg", entity_type="MyPolicyStore::Photo"
                        ),
                    )
                ),
                policy_store_id=str(cfn_policy_store.attr_policy_store_id),
            )

        with open("./policy/read_policy_template.cedar") as policy_template_file:
            read_photo_policy_template = verifiedpermissions.CfnPolicyTemplate(
                self,
                "ReadPhotoTemplate",
                statement=policy_template_file.read(),
                # the properties below are optional
                policy_store_id=str(cfn_policy_store.attr_policy_store_id),
            )

            cfn_policy = verifiedpermissions.CfnPolicy(
                self,
                "ReadPhotoTemplatePolicy",
                definition=verifiedpermissions.CfnPolicy.PolicyDefinitionProperty(
                    template_linked=verifiedpermissions.CfnPolicy.TemplateLinkedPolicyDefinitionProperty(
                        policy_template_id=str(
                            read_photo_policy_template.attr_policy_template_id
                        ),
                        # the properties below are optional
                        resource=verifiedpermissions.CfnPolicy.EntityIdentifierProperty(
                            entity_id="sunset.jpg", entity_type="MyPolicyStore::Photo"
                        ),
                    )
                ),
                policy_store_id=str(cfn_policy_store.attr_policy_store_id),
            )

        with open("./policy/delete_photo_static.cedar") as policy_file:
            cfn_policy = verifiedpermissions.CfnPolicy(
                self,
                "DeletePhotoStaticPolicy",
                definition=verifiedpermissions.CfnPolicy.PolicyDefinitionProperty(
                    static=verifiedpermissions.CfnPolicy.StaticPolicyDefinitionProperty(
                        statement=policy_file.read()
                    )
                ),
                policy_store_id=str(cfn_policy_store.attr_policy_store_id),
            )

        cfn_identity_source = verifiedpermissions.CfnIdentitySource(
            self,
            "MyCfnIdentitySource",
            configuration=verifiedpermissions.CfnIdentitySource.IdentitySourceConfigurationProperty(
                cognito_user_pool_configuration=verifiedpermissions.CfnIdentitySource.CognitoUserPoolConfigurationProperty(
                    user_pool_arn="arn:aws:cognito-idp:us-east-1:465283423899:userpool/us-east-1_aGGF5og07",
                    client_ids=["6s7q455t0knjthkqto91q7dnr1"],
                    group_configuration=verifiedpermissions.CfnIdentitySource.CognitoGroupConfigurationProperty(
                        group_entity_type="MyPolicyStore::UserGroup"
                    ),
                )
            ),
            policy_store_id=str(cfn_policy_store.attr_policy_store_id),
            # the properties below are optional
            principal_entity_type="MyPolicyStore::User",
        )

        CfnOutput(
            self,
            "PolicyStoreId",
            value=f"{cfn_policy_store.attr_policy_store_id}",
            description="Policy Store ID",
        )
