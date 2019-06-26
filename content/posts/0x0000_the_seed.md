---
title: "0x0000 The Seed"
date: 2019-05-07T01:37:07+01:00
draft: false
toc: false
images:
tags:
 - filler
 - random
 - hugo
 - github
---

Sometimes we need something and we can't find a straight up how-to online.  

We put a few pieces together, get it done but wonder if we ever need to do it again, will we find the same resources again? Will they be up? Will we follow the same links?  

We want to record our steps to remember later on, but we also want Google to index them so we get there, so why not post them up somewhere?

Internet is not running out of space.

In my case, I decided to dump everything here, RPG.

I'll start with how to set up a blog like this one:

* [Hugo](https://gohugo.io)
* on [Github Pages](https://pages.github.com/)
* ... with [custom CNAME](https://help.github.com/en/articles/using-a-custom-domain-with-github-pages)
* published by [Travis CI](https://travis-ci.org/)

## Step 1 - Hugo quickstart

Follow [Hugo quick.start](https://gohugo.io/getting-started/quick-start/) to get a basic page running.

```
➜  hugo new site quickstart
Congratulations! Your new Hugo site is created in quickstart.

Just a few more steps and you're ready to go:

1. Download a theme into the same-named folder.
   Choose a theme from https://themes.gohugo.io/, or
   create your own with the "hugo new theme <THEMENAME>" command.
2. Perhaps you want to add some content. You can add single files
   with "hugo new <SECTIONNAME>/<FILENAME>.<FORMAT>".
3. Start the built-in live server via "hugo server".

Visit https://gohugo.io/ for quickstart guide and full documentation.
➜  cd quickstart
➜  git init
Initialized empty Git repository in quickstart/.git/
➜  git submodule add https://github.com/budparr/gohugo-theme-ananke.git themes/ananke
Cloning into 'quickstart/themes/ananke'...
remote: Enumerating objects: 17, done.
remote: Counting objects: 100% (17/17), done.
remote: Compressing objects: 100% (15/15), done.
remote: Total 1349 (delta 3), reused 13 (delta 2), pack-reused 1332
Receiving objects: 100% (1349/1349), 4.14 MiB | 3.08 MiB/s, done.
Resolving deltas: 100% (722/722), done.
➜  echo theme = \"ananke\" >> config.toml
➜  hugo new posts/my-first-post.md
quickstart/content/posts/my-first-post.md created
```

If you run `hugo server -D` you should be able to open up http://localhost:1313/ and check your brand new blog with one empty post.

## Step 2 - Github pages

* Create a [GitHub](https://github.com/) repository
* Add it to your local repo and push
```
➜  git remote add origin git@github.com:YOURUSER/YOURREPO.git
➜  git push -u origin master
```
* Publish the site to branch `gh-pages`
```
➜  hugo -d /tmp/whatever
➜  git checkout --orphan gh-pages
➜  rm -fr *
➜  rm .gitmodules
➜  cp -a /tmp/whatever/* .
➜  git add .
➜  git push -u origin gh-pages
```
* Go to your GitHub project settings and enable `GitHub Pages` with `gh-pages branch` as `source`

After a couple of minutes _your brand new blog wit one empty post_ should be available at https://YOURUSER.github.io/YOURREPO

## Step 3 - EXTRA - Custom CNAME

If you'd rather use your own (sub)domain (such as https://rpg.skmobi.com/):

* Add the (sub)domain to a file named `CNAME` in the root of the master branch like [this](https://github.com/fopina/rpg/blob/master/CNAME)
* Setup your DNS with CNAME record pointing to `YOURUSER.github.io`
* As GitHub pages now supports HTTPS on custom domains (using [LetsEncrypt](https://letsencrypt.org/)), I'd recommend ticking `Enforce HTTPS` in `GitHub Pages` section of the project settings

## Step 4 - Travis-CI

As the last step, you can use [Travis-CI](https://travis-ci.org/) to automate publishing when pushing new Hugo content.
Original idea taken from [this post](https://www.sidorenko.io/post/2018/12/hugo-on-github-pages-with-travis-ci/).

* (Optionally) Create a second (bot) GitHub account and add it as collaborator of your repository. This allows you to add this account credentials to Travis instead of your main one.
* Signup to [Travis-CI](https://travis-ci.org/) and enable it for your repository
https://www.sidorenko.io/post/2018/12/hugo-on-github-pages-with-travis-ci/
* In `Environment Variables` of `Settings` of this Travis project, create the variable `GITHUB_AUTH_SECRET` with the content `https://USERNAME:PASSWORD@github.com/YOURUSER/YOURREPO`. Use your bot account here if you decided to create one.
* Create the file `deploy.sh` in your `master` branch root

```bash
#!/bin/bash

set -e

echo $GITHUB_AUTH_SECRET > ~/.git-credentials && chmod 0600 ~/.git-credentials
git config --global credential.helper store
git config --global user.email "GITHUB_USER@users.noreply.github.com"
git config --global user.name "Publishing bot"
git config --global push.default simple

git fetch origin gh-pages
git checkout FETCH_HEAD
git checkout -b gh-pages
rm -fr *
mv ../public/* .
rmdir ../public/
git add -A
git commit -m "rebuilding site on `date`, commit ${TRAVIS_COMMIT} and job ${TRAVIS_JOB_NUMBER}" || true
git push origin gh-pages
```
* And finally, the `.travis.yml`, also in your `master` branch root

```yaml
language: minimal

install:
  - wget -O /tmp/hugo.deb https://github.com/gohugoio/hugo/releases/download/v0.55.0/hugo_0.55.0_Linux-64bit.deb
  - sudo dpkg -i /tmp/hugo.deb

script:
  - hugo -d ../public
  - cp CNAME ../public

deploy:
  - provider: script
    script: ./deploy.sh
    skip_cleanup: true
    on:
      branch: master
```

Commit these 2 files, push them and you're done! Travis job should kick off and `gh-pages` branch will be automatically updated, as will your blog.
