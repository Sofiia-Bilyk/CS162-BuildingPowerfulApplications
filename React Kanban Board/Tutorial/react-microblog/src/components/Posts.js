import { useState, useEffect } from 'react';
import Spinner from 'react-bootstrap/Spinner';
import { useApi } from '../contexts/ApiProvider';
import More from './More';

export default function Posts() {
  const [posts, setPosts] = useState();
  const [pagination, setPagination] = useState();
  const api = useApi();

  useEffect(() => {
    (async () => {
      const response = await api.get('/feed');
      if (response.ok) {
        setPosts(response.body.data);
        setPagination(response.body.pagination);
      }
      else {
        setPosts(null);
      }
    })();
  }, [api]);

  const loadNextPage = async () => {
    const response = await api.get('/feed', {
      after: posts[posts.length - 1].timestamp
    });
    if (response.ok) {
      setPosts([...posts, ...response.body.data]);
      setPagination(response.body.pagination);
    }
  };

  let content;
  if (posts === undefined) {
    content = <Spinner animation="border" />;
  }
  else if (posts === null) {
    content = <p>Could not retrieve blog posts.</p>;
  }
  else if (posts.length === 0) {
    content = <p>There are no blog posts.</p>;
  }
  else {
    content = (
      <>
        {posts.map(post => {
          return (
            <p key={post.id}>
              <b>{post.author.username}</b> &mdash; {post.timestamp}
              <br />
              {post.text}
            </p>
          );
        })}
        <More pagination={pagination} loadNextPage={loadNextPage} />
      </>
    );
  }

  return content;
}
