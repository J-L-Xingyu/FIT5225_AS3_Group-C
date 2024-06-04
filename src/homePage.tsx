import React, { useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

const HomePage = () => {
    const navigate = useNavigate();
    const [file, setFile] = useState(null);
    const [deleteUrls, setDeleteUrls] = useState('');
    const [searchResults, setSearchResults] = useState([]);
    const [tagInput, setTagInput] = useState('');
    const [thumbnails, setThumbnails] = useState([]);
    const [smallUrl, setSmallUrl] = useState('');
    const [fullSizeImages, setFullSizeImages] = useState([]);
    const [fullSizeImages2, setFullSizeImages2] = useState([]);
    const [imageUrl, setImageUrl] = useState('');
    const [relatedImages, setRelatedImages] = useState([]);
    const [urls, setUrls] = useState('');
    const [tags, setTags] = useState('');
    const [operationType, setOperationType] = useState(1); // Default to adding tags
    const [subscribedTags, setSubscribedTags] = useState('');

    // 处理订阅标签变化
    const handleTagSubscriptionChange = (e) => {
        setSubscribedTags(e.target.value);
    };

    // 提交订阅的标签
    const submitTagSubscription = async () => {
        const email = sessionStorage.getItem('userEmail');
        if (!email) {
            alert('User email not available, please sign in again.');
            return;
        }

        const tagsArray = subscribedTags.split(',').map(tag => tag.trim());
        try {
            const data = {
                useremail: email,
                tags: tagsArray
            };
            console.log(data)
            const response = await axios.post('https://sywvaj35nf.execute-api.us-east-1.amazonaws.com/tryy/editsubtag', {body:JSON.stringify(data)}, {
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            alert('Subscribed successfully!');
        } catch (error) {
            console.log("error:",error)
            alert('Update Subscription successfully!');
        }
    };
    // Handle file selection
    const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        if (event.target.files) {
            setFile(event.target.files[0]);
        }
    };

    // Encode the image to Base64
    const encodeImage = (file: File): Promise<string> => new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = () => {
            if (typeof reader.result === 'string') {
                resolve(reader.result.split(',')[1]);
            } else {
                reject(new Error('FileReader result is not a string'));
            }
        };
        reader.onerror = error => reject(error);
        reader.readAsDataURL(file);
    });

    // Upload image to the server
    const uploadImage = async () => {
        if (!file) {
            alert('Please select a file!');
            return;
        }

        // 获取用户邮箱
        const email = sessionStorage.getItem('userEmail');
        if (!email) {
            alert('User email not available, please sign in again.');
            return;
        }

        try {
            const base64Image = await encodeImage(file);

            const data = {
                name: file.name,
                image: base64Image,
                useremail: email // 添加邮箱到发送的数据中
            };

            console.log("Data being sent:", data);
            const response = await axios.post('https://11iyoxqny6.execute-api.us-east-1.amazonaws.com/dev/upload', JSON.stringify(data), {
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            // const response = await axios.post('https://flcdfnzlv1.execute-api.us-east-1.amazonaws.com/dev/upload', JSON.stringify(data), {
            //     headers: {
            //         'Content-Type': 'application/json'
            //     }
            // });
            alert('Image uploaded successfully!');
            console.log("Data being sent:");
            console.log('Response;;:', response.data);
        } catch (error) {
            alert('Failed to upload image');
            console.error('Error:', error);
        }
    };



    // Search images based on tags
    const searchByTags = async () => {
        const tagsArray = tagInput.split(',').map(tag => {
            const parts = tag.split(':').map(part => part.trim());
            return { tags: parts[0], counts: parseInt(parts[1] || "1", 10) };
        });
        // 获取用户邮箱
        const email = sessionStorage.getItem('userEmail');
        if (!email) {
            alert('User email not available, please sign in again.');
            return;
        }
        const data = {
            tags: tagsArray.map(tag => tag.tags),
            counts: tagsArray.map(tag => tag.counts),
            useremail: email
        };

        try {
            const response = await axios.post('https://6qsr8t0we8.execute-api.us-east-1.amazonaws.com/dev/search1', data, {
                    headers: {
                        'Content-Type': 'applicat-ion/json'
                    }
                });
            // const response = await axios.post('https://6ntul656ma.execute-api.us-east-1.amazonaws.com/dev/search', data, {
            //     headers: {
            //         'Content-Type': 'applicat-ion/json'
            //     }
            // });
            const imageUrls = response.data.links;
            const imagesArray = Array.isArray(imageUrls) ? imageUrls : [imageUrls];
            setThumbnails(imagesArray);
            if(imageUrls.length>0){alert("get image successfully")}else {alert("no image found")}
            // setThumbnails(response.data.links)
        } catch (error) {
            console.log("data",data);
            alert('Failed to search by tags');
        }
    };

    // Search full-size images by thumbnail URL
    const searchBySmallUrl = async () => {
        try {
            console.log(smallUrl)
            const response = await axios.get(`https://6qsr8t0we8.execute-api.us-east-1.amazonaws.com/dev/search2?thumbnail_url=${smallUrl}`);
            // const response = await axios.get(`https://6ntul656ma.execute-api.us-east-1.amazonaws.com/dev/search2?thumbnail_url=${smallUrl}`);
            const imageUrls = response.data.image_url;
            const imagesArray = Array.isArray(imageUrls) ? imageUrls : [imageUrls];
            setFullSizeImages(imagesArray);
            if(imageUrls.length>0){alert("get image successfully")}else {alert("no image found")}
        } catch (error) {
            console.log(error)
            alert('Failed to search by thumbnail URL');
        }
    };

    // Search images by the tags of an image
    const searchImagewithSameTags = async () => {
        if (!file) {
            alert('Please select a file!');
            return;
        }

        // 获取用户邮箱
        const email = sessionStorage.getItem('userEmail');
        if (!email) {
            alert('User email not available, please sign in again.');
            return;
        }

        try {
            const base64Image = await encodeImage(file);

            const data = {
                name: file.name,
                image: base64Image,
                useremail: email // 添加邮箱到发送的数据中
            };

            console.log("Data being sent:", data);
            const response = await axios.post('https://6qsr8t0we8.execute-api.us-east-1.amazonaws.com/dev/search3', JSON.stringify(data), {
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            // const response = await axios.post('https://flcdfnzlv1.execute-api.us-east-1.amazonaws.com/dev/upload', JSON.stringify(data), {
            //     headers: {
            //         'Content-Type': 'application/json'
            //     }
            // });
            // alert('Image uploaded successfully!');
            const imageUrls = response.data.links;
            console.log("images getted:",imageUrls)
            const imagesArray = Array.isArray(imageUrls) ? imageUrls : [imageUrls];
            setFullSizeImages2(imagesArray);
            if(imageUrls.length>0){alert("get image successfully")}else {alert("no image found")}
        } catch (error) {
            alert('Failed to upload image');
            console.error('Error:', error);
        }
    };

    // Manual addition or removal of tags
    const handleUrlsChange = (e) => {
        setUrls(e.target.value);
    };
    const handleTagsChange = (e) => {
        setTags(e.target.value);
    };
    const handleOperationChange = (e) => {
        setOperationType(e.target.value);
    };
    const submitTags = async () => {
        const urlList = urls.split(',');
        const tagList = tags.split(',');
        try {
            const data = {
                url: urlList.map(url => url.trim()),
                type: operationType,
                tags: tagList.map(tag => tag.trim())
            };
            console.log("data to be sent",data)
            // const response = await axios.post('https://x9e14b321g.execute-api.us-east-1.amazonaws.com/dev/search4', data, {
            //     headers: {
            //         'Content-Type': 'application/json'
            //     }
            // });
            const response = await axios.post('https://6qsr8t0we8.execute-api.us-east-1.amazonaws.com/dev/search4', data, {
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            alert('Tags updated successfully!');
        } catch (error) {
            alert('Failed to update tags: ' + error.message);
        }
    };


    // Delete images
    const deleteImages = async () => {
        const urlList = deleteUrls.split(',');
        try {
            const data = {
                urls: urlList.map(url => url.trim())
            };
            console.log("data",data)
            const response = await axios.post('https://6qsr8t0we8.execute-api.us-east-1.amazonaws.com/dev/delete', data, {
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            // const response = await axios.post('https://6ntul656ma.execute-api.us-east-1.amazonaws.com/search4/delete', data, {
            //     headers: {
            //         'Content-Type': 'application/json'
            //     }
            // });
            alert('Images deleted successfully');
        } catch (error) {
            alert('Failed to delete images');
        }
    };

    // Handle logout
    const handleLogout = () => {
        navigate('/login');
    };

    return (
        <div>
            <h1>Image Detection System</h1>
            {/* Update Subscription */}
            <h2>Update Subscription</h2>
            <input
                type="text"
                value={subscribedTags}
                onChange={handleTagSubscriptionChange}
                placeholder="Enter tags to subscribe, separated by commas"
            />
            <button onClick={submitTagSubscription}>Subscribe</button>
            {/* Upload Image */}
            <h2>Upload Image</h2>
            <input type="file" onChange={handleFileChange} />
            <button onClick={uploadImage}>Upload Image</button>

            {/* Search by Tags */}
            <h2>1. Search Images Based on Tags</h2>
            <input
                type="text"
                value={tagInput}
                onChange={e => setTagInput(e.target.value)}
                placeholder="Enter tags and counts (e.g., cat:1, car:2)"
            />
            <button onClick={searchByTags}>Search by Tags</button>
            <div>
                {thumbnails.map((thumbnail, index) => (
                    <div key={index}>
                    <img key={index} src={thumbnail} alt="Thumbnail" style={{ width: '100px', height: 'auto' }} onClick={() => window.open(thumbnail, '_blank')} />
                        <p>{"Thumbnail URL: "+thumbnail}</p>
                    </div>
                        ))}

            </div>

             {/*Search by Thumbnail URL */}
            <h2>2. Search Images Based on the Thumbnail's URL</h2>
            <input
                type="text"
                value={smallUrl}
                onChange={e => setSmallUrl(e.target.value)}
                placeholder="Enter thumbnail URL"
            />
            <button onClick={searchBySmallUrl}>Search by Thumbnail URL</button>
            <div>
                {fullSizeImages.map((image_url, index) => (
                    <div key={index}>
                        <img src={image_url} alt="Full Size" style={{ width: '200px', height: 'auto', margin: '10px' }} />
                        <p>{"Image URL: "+image_url}</p>
                    </div>
                ))}
            </div>

            {/* Search Images with same Tags*/}
            <h2>3. Search Images with same Tags</h2>
            <input type="file" onChange={handleFileChange} />
            <button onClick={searchImagewithSameTags}>Search Image</button>
            <div>
                {fullSizeImages2.map((image_url, index) => (
                    <div key={index}>
                        <img key={index} src={image_url} alt="Full Size" style={{ width: '100px', height: 'auto' }} onClick={() => window.open(image_url, '_blank')} />
                        <p>{"Image URL: "+image_url}</p>
                    </div>
                ))}
            </div>

            {/* Manual Addition or Removal of Tags */}
            <h2>4. Manual Addition or Removal of Tags</h2>
            <textarea
                value={urls}
                onChange={handleUrlsChange}
                placeholder="Enter image URLs, separated by commas"
            />
            <textarea
                value={tags}
                onChange={handleTagsChange}
                placeholder="Enter tags, separated by commas"
            />
            <select value={operationType} onChange={handleOperationChange}>
                <option value={1}>Add</option>
                <option value={0}>Remove</option>
            </select>
            <button onClick={submitTags}>Submit</button>

            {/* Delete Images */}
            <h2>5. Delete Images</h2>
            <input
                type="text"
                value={deleteUrls}
                onChange={e => setDeleteUrls(e.target.value)}
                placeholder="Enter thumbnail URLs to delete, separated by commas"
            />
            <button onClick={deleteImages}>Delete Images</button>

            {/* Logout */}
            <button onClick={handleLogout}>Logout</button>

            {searchResults.map((url, index) => (
                <div key={index}>
                    <p>{url}</p>
                </div>
            ))}
        </div>
    );
};

export default HomePage;
