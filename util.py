def can_get_gem(all_gems, gems):
    for gem_t, cnt in gems.items():
        if cnt > all_gems[gem_t]:
            return False
    return True
