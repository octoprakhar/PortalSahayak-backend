from supabase import Client

class Storage:
    """
    It will help in doing all CRUD related activity with file storage 
    
    Parameter:
        client: Client(database client)

    """

    def __init__(self, client: Client):
        self.client = client

    def _bucket_exists(self, bucket_name: str) -> bool:
        buckets = self.client.storage.list_buckets()
        return any(bucket.name == bucket_name for bucket in buckets)

    def upload(self, bucket_name: str, local_file: str, remote_path: str, upsert: bool = False) -> str:
        """
        Upload the file in the bucket.

        Parameter:
            bucket_name: Name of the bucket(it must be already made) we need to upload
            local_file: Path of the file where it is stored locally
            remote_file: Path of the file we need to make inside that bucket
            upsert: bool = Do we need to overwrite if same filename comes again

        Returns:
            Remote file path, that we can work on

        """

        if not self._bucket_exists(bucket_name):
            raise ValueError(
                f"Bucket '{bucket_name}' does not exist."
            )

        with open(local_file, "rb") as f:
            self.client.storage.from_(bucket_name).upload(
                path=remote_path,
                file=f,
                file_options={
                    "upsert": str(upsert).lower()
                }
            )

        return remote_path



