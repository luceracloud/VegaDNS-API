from peewee import CharField, IntegerField, PrimaryKeyField

from vegadns.api.models import database, BaseModel
from vegadns.api.models.record import Record
from vegadns.validate.dns import ValidateDNS


class Domain(BaseModel):
    domain = CharField(unique=True)
    domain_id = PrimaryKeyField()
    group_owner_id = IntegerField(
        db_column='group_owner_id', null=True, default=0
    )
    owner_id = IntegerField(db_column='owner_id', null=True, default=0)
    status = CharField(default="active")

    class Meta:
        db_table = 'domains'

    # For removing unused group_owner field via self.to_clean_dict()
    clean_keys = ["group_owner_id"]

    def validate(self):
        if self.status not in ["active", "inactive"]:
            raise ValueError("status must be either 'active' or 'inactive'")

        if not ValidateDNS.record_hostname(self.domain):
            raise ValueError("domain is invalid: " + self.domain)

    def get_records(self):
        if not self.domain_id:
            raise Exception("Cannot get records, domain_id is not set")

        return Record.select(Record).where(
            Record.domain_id == self.domain_id
        )
