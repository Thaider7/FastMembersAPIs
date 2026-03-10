from fastapi import FastAPI, HTTPException
import pandas as pd
import git
app = FastAPI(title="Gym Members API")

# Load Excel
df = pd.read_excel("gym_members.xlsx")

df = df.fillna('')  # Replace NaN with empty string for JSON serialization
df["JoinDate"] = df["JoinDate"].astype(str)

# Initialize Git repo
repo = git.Repo('.')

# Helper to save changes
def save_excel():
    df.to_excel("gym_members.xlsx", index=False)

# Helper to commit changes
def commit_changes(message):
    repo.index.add(['gym_members.xlsx'])
    repo.index.commit(message)
    try:
        origin = repo.remote(name='origin')
        origin.push()
    except Exception as e:
        print(f"Push failed: {e}")  # For debugging, but in API, perhaps log

@app.get("/members")
def get_all_members(skip: int = 0, limit: int = 50):
    total = len(df)
    data = df.iloc[skip:skip+limit].to_dict(orient="records")
    return {"data": data, "skip": skip, "limit": limit, "total": total}

@app.get("/member/{member_id}")
def get_member(member_id: int):
    member = df[df["MemberID"] == member_id]
    if member.empty:
        raise HTTPException(status_code=404, detail="Member not found")
    result = member.to_dict(orient="records")[0]

# convert JoinDate to string
    result["JoinDate"] = str(result["JoinDate"])

    return result


@app.post("/member/")
def add_member(member: dict):
    if "MemberID" not in member:
        member["MemberID"] = df["MemberID"].max() + 1
    df.loc[len(df)] = member
    save_excel()
    commit_changes(f"Added new member: {member['MemberID']}")
    return {"msg": "Member added", "MemberID": member["MemberID"]}

@app.put("/member/{member_id}")
def update_member(member_id: int, updates: dict):
    idx = df.index[df["MemberID"] == member_id].tolist()
    if not idx:
        raise HTTPException(status_code=404, detail="Member not found")
    for key, value in updates.items():
        df.at[idx[0], key] = value
    save_excel()
    commit_changes(f"Updated member: {member_id}")
    return {"msg": "Member updated"}

@app.delete("/member/{member_id}")
def delete_member(member_id: int):
    idx = df.index[df["MemberID"] == member_id].tolist()
    if not idx:
        raise HTTPException(status_code=404, detail="Member not found")
    df.drop(idx[0], inplace=True)
    save_excel()
    commit_changes(f"Deleted member: {member_id}")
    return {"msg": "Member deleted"}

@app.delete("/member/{member_id}")
def delete_member(member_id: int):
    idx = df.index[df["MemberID"] == member_id].tolist()
    if not idx:
        raise HTTPException(status_code=404, detail="Member not found")
    df.drop(idx[0], inplace=True)
    save_excel()
    commit_changes(f"Deleted member: {member_id}")
    return {"msg": "Member deleted"}