def get_post_list_cache_key() -> str:
    return "blog:post:list"

def get_post_detail_cache_key(post_id: str) -> str:
    return f"blog:post:{post_id}"