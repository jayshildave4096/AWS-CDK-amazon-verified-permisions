from aws_cdk import (
    Stack,
    CfnOutput,
    aws_verifiedpermissions as verifiedpermissions
)
from constructs import Construct
import json

class AVPStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        with open("/Users/dave/Desktop/AWS/APP/schema1.json") as file:
            cfn_policy_store = verifiedpermissions.CfnPolicyStore(self, "MyPolicyStore",
                validation_settings=verifiedpermissions.CfnPolicyStore.ValidationSettingsProperty(
                    mode="STRICT"
                ),
                description="MyPolicyStore",
                schema=verifiedpermissions.CfnPolicyStore.SchemaDefinitionProperty(
                cedar_json=json.dumps(json.loads(file.read()))
                )

            )
        print(cfn_policy_store.attr_policy_store_id)  

        with open("/Users/dave/Desktop/AWS/APP/policy/policy_template.cedar") as policy_template_file:      
            cfn_policy_template = verifiedpermissions.CfnPolicyTemplate(self, "MyCfnPolicyTemplate",
                statement=policy_template_file.read(),

                # the properties below are optional
                policy_store_id=str(cfn_policy_store.attr_policy_store_id)
            )

        cfn_policy = verifiedpermissions.CfnPolicy(self, "AdminPolicy",
            definition=verifiedpermissions.CfnPolicy.PolicyDefinitionProperty(
                template_linked=verifiedpermissions.CfnPolicy.TemplateLinkedPolicyDefinitionProperty(
                    policy_template_id=str(cfn_policy_template.attr_policy_template_id),

                    # # the properties below are optional
                    principal=verifiedpermissions.CfnPolicy.EntityIdentifierProperty(
                        entity_id="jayshil",
                        entity_type="MyPolicyStore::User"
                    ),
                    resource=verifiedpermissions.CfnPolicy.EntityIdentifierProperty(
                        entity_id="sunset.jpg",
                        entity_type="MyPolicyStore::Photo"
                    )
                )
            ),
            policy_store_id=str(cfn_policy_store.attr_policy_store_id)
        ) 

        with open("/Users/dave/Desktop/AWS/APP/policy/delete_photo.cedar") as policy_file:      
            cfn_policy = verifiedpermissions.CfnPolicy(self, "DeletePhotoPolicy",
                definition=verifiedpermissions.CfnPolicy.PolicyDefinitionProperty(
                    static=verifiedpermissions.CfnPolicy.StaticPolicyDefinitionProperty(
                        statement=policy_file.read()
                    )
                ),
                policy_store_id=str(cfn_policy_store.attr_policy_store_id)
            )   
        

        CfnOutput(self, "PolicyStoreId", 
            value=f"{cfn_policy_store.attr_policy_store_id}",
            description="Policy Store ID"
        )
        

