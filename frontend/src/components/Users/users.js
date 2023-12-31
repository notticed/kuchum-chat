import React, { useEffect, useState } from "react";

export const Users = () => {
  const [data, setData] = useState(null)
  const [isLoading, setLoading] = useState(false)
  useEffect(() => {
    setLoading(true)
    fetch('https://chat-backend-86jx.onrender.com/api/users')
      .then(res => res.json())
      .then(data => {
        setData(data)
        setLoading(false)
      })
  }, [])


  if (data != null){
  return (
    <>
    <h1 className="title_text">Users</h1>
    {data.map(user => <li key={user.nick}>{user.nick}, {user._id}</li>)}
    </>
  )}


}



