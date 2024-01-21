def build_related_comments_struct(comments: list[dict]) -> list[dict]:
    comments.sort(key=lambda x: (-1 if x["answer_to"] is None else x["answer_to"]))
    proxy_ids = {}  # to represent relations of every comment to mother model
    out_comments = {
        comment["id"]: comment for comment in comments if comment["answer_to"] is None
    }
    for comment in comments:
        if comment["answer_to"] is None:
            continue
        if comment["answer_to"] in out_comments:
            out_comments[comment["answer_to"]].setdefault("subcomments", []).append(
                comment
            )
            proxy_ids[comment["id"]] = comment["answer_to"]
        else:
            out_comments[proxy_ids[comment["answer_to"]]].setdefault(
                "subcomments", []
            ).append(comment)
            proxy_ids[comment["id"]] = proxy_ids[comment["answer_to"]]

    return list(out_comments.values())
