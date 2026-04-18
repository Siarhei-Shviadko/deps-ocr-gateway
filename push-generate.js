const { writeFileSync} = require('fs');
const list = ['', '-aws-textract', '-azure-form-recognizer', '-gcp-vision', '-tesseract'];

let config = `
stages:
  - push
  - deploy
`;

for(let part of list) {

config += `

push${part}:
  stage: push
  tags:
  - kubernetes
  interruptible: true
  extends:
    - .base
    - .default-retry
  variables:
    SOURCE_VERSION: "ci"
  script:
    - echo "$PWD"
    - make version=\$SOURCE_VERSION name=${part} tag=\${CI_COMMIT_SHORT_SHA:-1.0.0} pull
    - make version=\$SOURCE_VERSION name=${part} tag=\${CI_COMMIT_SHORT_SHA:-1.0.0} new_version=\$TARGET_VERSION new_tag=\${CI_COMMIT_SHORT_SHA:-1.0.0} tag
    - make version=\$TARGET_VERSION name=${part} tag=\${CI_COMMIT_SHORT_SHA:-1.0.0} push
    - make version=\$SOURCE_VERSION name=${part} tag=\${CI_COMMIT_SHORT_SHA:-1.0.0} new_version=\$PLATFORM_VERSION new_tag=\${CI_COMMIT_SHORT_SHA:-1.0.0} tag
    - make version=\$PLATFORM_VERSION name=${part} tag=\${CI_COMMIT_SHORT_SHA:-1.0.0} push
  after_script:
    - docker-compose down -v

`;

}

config +=  `
deploy:
  stage: deploy
  extends:
  - .k8s-defaults
  variables:
    COMMAND: "helm-upgrade"

`
;

writeFileSync('./push-gitlab-ci.yml', config, {encoding: 'utf-8'});
