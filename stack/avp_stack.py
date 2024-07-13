from aws_cdk import Stack, CfnOutput, aws_verifiedpermissions as verifiedpermissions
from constructs import Construct
import json
import os


class AVPStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create policy store with schema file
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

        # Create policy template for creating photos
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

        # Create policy template to read photos
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

        # Create static policy for deleting photos
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

        CfnOutput(
            self,
            "PolicyStoreId",
            value=f"{cfn_policy_store.attr_policy_store_id}",
            description="Policy Store ID",
        )
